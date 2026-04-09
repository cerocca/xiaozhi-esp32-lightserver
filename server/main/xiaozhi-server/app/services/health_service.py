from urllib.parse import urlparse, urlunparse

import requests

from core.utils.config_normalizer import resolve_llm_config


def _get_provider_config(config, module_name):
    selected = config.get("selected_module", {}).get(module_name)
    providers = config.get(module_name, {})
    return providers.get(selected, {}) if selected else {}


def _normalize_http_url(url, path=""):
    if not url:
        return None
    parsed = urlparse(str(url).strip())
    if not parsed.scheme or not parsed.netloc:
        return None
    scheme = "https" if parsed.scheme in ("https", "wss") else "http"
    return urlunparse((scheme, parsed.netloc, path or parsed.path or "/", "", "", ""))


def _build_http_result(status, reason, http_status=None, endpoint=None):
    return {
        "status": status,
        "reason": reason,
        "http_status": http_status,
        "endpoint": endpoint,
    }


def _check_http_endpoint(url, headers=None):
    if not url:
        return _build_http_result("error", "connection_error", endpoint=url)
    try:
        response = requests.get(
            url,
            timeout=0.5,
            allow_redirects=False,
            headers=headers or {"User-Agent": "health-check"},
        )
        status_code = response.status_code
        if status_code in (401, 403):
            return _build_http_result(
                "error", "auth_error", http_status=status_code, endpoint=url
            )
        if status_code >= 500:
            return _build_http_result(
                "error", "http_error", http_status=status_code, endpoint=url
            )
        return _build_http_result("ok", "ok", http_status=status_code, endpoint=url)
    except requests.Timeout:
        return _build_http_result("error", "timeout", endpoint=url)
    except requests.ConnectionError:
        return _build_http_result("error", "connection_error", endpoint=url)
    except requests.RequestException:
        return _build_http_result("error", "connection_error", endpoint=url)


def check_llm(config):
    provider_config = resolve_llm_config(config)
    base_url = provider_config.get("base_url")
    api_key = provider_config.get("api_key")
    url = _normalize_http_url(base_url)
    if not url:
        return _build_http_result("error", "connection_error", endpoint=url)
    if url.endswith("/"):
        url = url.rstrip("/")
    url = url + "/models"
    headers = {"User-Agent": "health-check"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return _check_http_endpoint(url, headers=headers)


def check_asr(config):
    provider_config = _get_provider_config(config, "ASR")
    url = _normalize_http_url(
        provider_config.get("base_url")
        or provider_config.get("api_url")
        or provider_config.get("url")
    )
    return _check_http_endpoint(url)


def check_tts(config):
    provider_config = _get_provider_config(config, "TTS")
    base_url = (
        provider_config.get("base_url")
        or provider_config.get("api_url")
        or provider_config.get("url")
    )
    health_url = _normalize_http_url(base_url, "/health")
    health_result = _check_http_endpoint(health_url)
    if health_result["status"] == "ok":
        return health_result
    url = _normalize_http_url(base_url)
    return _check_http_endpoint(url)


def check_device(server=None):
    ws_server = getattr(server, "_ws_server", None)
    connections = getattr(ws_server, "connections", None)
    is_connected = bool(connections)
    return {
        "status": "connected" if is_connected else "disconnected",
        "reason": "connected" if is_connected else "disconnected",
        "last_seen": None,
        "connection_duration": None,
    }
