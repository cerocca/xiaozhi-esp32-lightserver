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


def _is_endpoint_alive(url, headers=None):
    if not url:
        return False
    try:
        response = requests.get(
            url,
            timeout=0.5,
            allow_redirects=False,
            headers=headers or {"User-Agent": "health-check"},
        )
        return 100 <= response.status_code < 500
    except requests.RequestException:
        return False


def check_llm(config):
    provider_config = resolve_llm_config(config)
    base_url = provider_config.get("base_url")
    api_key = provider_config.get("api_key")
    url = _normalize_http_url(base_url)
    if not url:
        return "error"
    if url.endswith("/"):
        url = url.rstrip("/")
    url = url + "/models"
    headers = {"User-Agent": "health-check"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return "ok" if _is_endpoint_alive(url, headers=headers) else "error"


def check_asr(config):
    provider_config = _get_provider_config(config, "ASR")
    url = _normalize_http_url(
        provider_config.get("base_url")
        or provider_config.get("api_url")
        or provider_config.get("url")
    )
    return "ok" if _is_endpoint_alive(url) else "error"


def check_tts(config):
    provider_config = _get_provider_config(config, "TTS")
    base_url = provider_config.get("base_url") or provider_config.get("api_url") or provider_config.get("url")
    health_url = _normalize_http_url(base_url, "/health")
    if _is_endpoint_alive(health_url):
        return "ok"
    url = _normalize_http_url(base_url)
    return "ok" if _is_endpoint_alive(url) else "error"


def check_device(server=None):
    ws_server = getattr(server, "_ws_server", None)
    connections = getattr(ws_server, "connections", None)
    return "connected" if connections else "disconnected"
