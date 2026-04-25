import subprocess
from pathlib import Path
import httpx

from app.config import settings


def _run(cmd: list[str], cwd: str | None = None, timeout: int = 8) -> dict:
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as e:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
        }


def get_xiaozhi_status() -> dict:
    compose_file = Path(settings.xiaozhi_dir)
    exists = compose_file.exists()

    if not exists:
        return {
            "name": "xiaozhi-esp32-server",
            "exists": False,
            "healthy": False,
            "summary": f"Directory non trovata: {settings.xiaozhi_dir}",
            "details": "",
        }

    result = _run(["docker", "compose", "ps"], cwd=settings.xiaozhi_dir)

    return {
        "name": "xiaozhi-esp32-server",
        "exists": True,
        "healthy": result["ok"],
        "summary": "docker compose ps eseguito" if result["ok"] else "errore docker compose ps",
        "details": result["stdout"] or result["stderr"],
    }


def get_piper_status() -> dict:
    svc = settings.piper_service_name
    active = _run(["systemctl", "is-active", svc])
    enabled = _run(["systemctl", "is-enabled", svc])

    try:
        with httpx.Client(timeout=3.0) as client:
            r = client.get(settings.piper_health_url)
            health_ok = r.status_code == 200
            health_body = r.text.strip()
    except Exception as e:
        health_ok = False
        health_body = str(e)

    return {
        "name": svc,
        "active": active["stdout"],
        "enabled": enabled["stdout"],
        "healthy": active["stdout"] == "active" and health_ok,
        "summary": f"active={active['stdout']} enabled={enabled['stdout']}",
        "details": f"health: {health_body}",
    }


def get_config_status() -> dict:
    path = Path(settings.xiaozhi_config)
    return {
        "name": ".config.yaml",
        "exists": path.exists(),
        "healthy": path.exists() and path.is_file(),
        "summary": str(path),
        "details": f"size={path.stat().st_size} bytes" if path.exists() else "file non trovato",
    }


def get_dashboard_status() -> dict:
    return {
        "xiaozhi": get_xiaozhi_status(),
        "piper": get_piper_status(),
        "config": get_config_status(),
    }
