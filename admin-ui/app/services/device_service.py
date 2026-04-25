from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime

from app.services.log_service import get_xserver_logs


CONN_RE = re.compile(
    r"""INFO-(?P<ip>\d+\.\d+\.\d+\.\d+)\s+conn\s+-\s+Headers:\s+(?P<headers>\{.*\})"""
)
LISTEN_RE = re.compile(r'收到listen消息：(\{.*\})')
MCP_RE = re.compile(r'收到mcp消息：(\{.*\})')
DISCONNECT_RE = re.compile(r'客户端断开连接')


@dataclass
class DeviceRecord:
    device_id: str
    client_id: str = "-"
    ip: str = "-"
    session_id: str = "-"
    model: str = "-"
    version: str = "-"
    last_seen: str = "-"
    status: str = "unknown"
    last_event: str = "-"


def _extract_timestamp(line: str) -> str:
    m = re.match(r".*?\|\s+(\d{6}\s+\d{2}:\d{2}:\d{2})", line)
    if not m:
        return "-"
    raw = m.group(1)
    try:
        dt = datetime.strptime(raw, "%y%m%d %H:%M:%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return raw


def _load_json_fragment(fragment: str) -> dict | None:
    try:
        return json.loads(fragment)
    except Exception:
        return None


def _combined_log_text(lines: int) -> str:
    result = get_xserver_logs(lines)
    parts = []
    if result.get("stdout"):
        parts.append(result["stdout"])
    if result.get("stderr"):
        parts.append(result["stderr"])
    return "\n".join(parts)


def parse_devices_from_logs(lines: int = 1000) -> list[dict]:
    text = _combined_log_text(lines)
    if not text.strip():
        return []

    devices: dict[str, DeviceRecord] = {}

    # mappa session_id -> device_id
    session_to_device: dict[str, str] = {}

    # ultimo device “attivo” visto nei log, utile come fallback
    last_device_id: str | None = None

    for line in text.splitlines():
        timestamp = _extract_timestamp(line)

        conn_match = CONN_RE.search(line)
        if conn_match:
            ip = conn_match.group("ip")
            headers_raw = conn_match.group("headers")

            # i log usano dict Python con apici singoli
            try:
                headers = eval(headers_raw, {"__builtins__": {}}, {})
            except Exception:
                headers = {}

            device_id = headers.get("device-id", "-")
            client_id = headers.get("client-id", "-")

            if device_id not in devices:
                devices[device_id] = DeviceRecord(device_id=device_id)

            rec = devices[device_id]
            rec.ip = ip
            rec.client_id = client_id
            rec.last_seen = timestamp
            rec.status = "connected"
            rec.last_event = "conn"

            last_device_id = device_id
            continue

        listen_match = LISTEN_RE.search(line)
        if listen_match:
            payload = _load_json_fragment(listen_match.group(1))
            if payload:
                session_id = payload.get("session_id", "-")
                device_id = session_to_device.get(session_id, last_device_id)

                if device_id:
                    if device_id not in devices:
                        devices[device_id] = DeviceRecord(device_id=device_id)

                    rec = devices[device_id]
                    rec.session_id = session_id
                    rec.last_seen = timestamp
                    rec.status = "connected"
                    rec.last_event = "listen"
                    session_to_device[session_id] = device_id
            continue

        mcp_match = MCP_RE.search(line)
        if mcp_match:
            payload = _load_json_fragment(mcp_match.group(1))
            if payload:
                session_id = payload.get("session_id", "-")
                device_id = session_to_device.get(session_id, last_device_id)

                if device_id:
                    if device_id not in devices:
                        devices[device_id] = DeviceRecord(device_id=device_id)

                    rec = devices[device_id]
                    rec.session_id = session_id
                    rec.last_seen = timestamp
                    rec.status = "connected"
                    rec.last_event = "mcp"
                    session_to_device[session_id] = device_id

                    server_info = (
                        payload.get("payload", {})
                        .get("result", {})
                        .get("serverInfo", {})
                    )
                    if server_info:
                        rec.model = server_info.get("name", rec.model)
                        rec.version = server_info.get("version", rec.version)
            continue

        if DISCONNECT_RE.search(line):
            if last_device_id and last_device_id in devices:
                rec = devices[last_device_id]
                rec.last_seen = timestamp
                rec.status = "disconnected"
                rec.last_event = "disconnect"
            continue

    records = [asdict(v) for v in devices.values()]
    records.sort(key=lambda x: x["last_seen"], reverse=True)
    return records
