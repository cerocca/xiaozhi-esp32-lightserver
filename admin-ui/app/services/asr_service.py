import re
from urllib.parse import urlsplit

import httpx
import yaml

from app.services.config_service import read_config_text, save_config


ASR_PRESETS = {
    "groq": {
        "label": "Groq",
        "type": "openai",
        "endpoint_field": "base_url",
        "endpoint": "https://api.groq.com/openai/v1/audio/transcriptions",
        "model": "whisper-large-v3-turbo",
        "api_key": "",
        "output_dir": "tmp/",
    },
    "openai_compatible": {
        "label": "OpenAI-compatible",
        "type": "openai",
        "endpoint_field": "base_url",
        "endpoint": "https://example.com/v1/audio/transcriptions",
        "model": "whisper-1",
        "api_key": "",
        "output_dir": "",
    },
}

PROFILE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _safe_load_config_data():
    try:
        content = read_config_text()
        data = yaml.safe_load(content) or {}
    except (OSError, yaml.YAMLError):
        return {}

    return data if isinstance(data, dict) else {}


def _load_config_data_for_update():
    try:
        content = read_config_text()
    except OSError as exc:
        return None, f"Unable to read the current config: {exc}"

    try:
        data = yaml.safe_load(content) or {}
    except yaml.YAMLError as exc:
        return None, f"Current config is invalid: {exc}"

    if not isinstance(data, dict):
        return None, "Current config is invalid: the YAML root must be a map"

    return data, ""


def _get_dict(data, key):
    value = data.get(key, {})
    return value if isinstance(value, dict) else {}


def _ensure_dict(data, key):
    value = data.get(key)
    if isinstance(value, dict):
        return value
    data[key] = {}
    return data[key]


def _sanitize_profile_name(value):
    return str(value or "").strip()


def _is_valid_profile_name(value):
    return bool(PROFILE_NAME_PATTERN.fullmatch(_sanitize_profile_name(value)))


def _profile_name_error(profile_name):
    return {
        "ok": False,
        "message": (
            f"Invalid profile name: {profile_name}. "
            "Use only letters, numbers, underscores (_), or hyphens (-)."
        ),
    }


def _get_model(block):
    if not isinstance(block, dict):
        return ""

    for key in ("model", "model_name"):
        value = str(block.get(key, "") or "").strip()
        if value:
            return value
    return ""


def _get_endpoint(block):
    if not isinstance(block, dict):
        return ""

    for key in ("api_url", "base_url"):
        value = str(block.get(key, "") or "").strip()
        if value:
            return value
    return ""


def _get_endpoint_field_name(block):
    if not isinstance(block, dict):
        return "base_url"

    has_api_url = bool(str(block.get("api_url", "") or "").strip())
    has_base_url = bool(str(block.get("base_url", "") or "").strip())
    if has_api_url and not has_base_url:
        return "api_url"
    return "base_url"


def _api_key_is_intentionally_not_needed(value):
    return str(value or "").strip().lower() == "not-needed"


def _guess_provider(profile_name, block):
    block = block if isinstance(block, dict) else {}
    endpoint = _get_endpoint(block).lower()
    model = _get_model(block).lower()

    for key in ("provider", "provider_name", "type"):
        value = str(block.get(key, "") or "").strip()
        if value:
            return value

    if "groq" in endpoint or "whisper-large-v3-turbo" in model:
        return "groq"

    return str(profile_name or "").strip()


def _is_local_endpoint(endpoint):
    normalized = str(endpoint or "").strip().lower()
    return normalized.startswith("http://127.0.0.1") or normalized.startswith("http://localhost")


def _asr_requires_api_key(endpoint):
    return bool(endpoint) and not _is_local_endpoint(endpoint)


def _validate_asr_profile(block):
    block = block if isinstance(block, dict) else {}
    warnings = []
    type_value = str(block.get("type", "") or "").strip()
    model = _get_model(block)
    endpoint = _get_endpoint(block)
    api_key = str(block.get("api_key", "") or "").strip()

    if not type_value:
        warnings.append("type mancante")
    if not model:
        warnings.append("model/model_name mancante")

    if type_value == "openai":
        if not endpoint:
            warnings.append("endpoint URL mancante")
        if (not endpoint or _asr_requires_api_key(endpoint)) and not api_key and not _api_key_is_intentionally_not_needed(api_key):
            warnings.append("api_key mancante")

    return {
        "validation_status": "ok" if not warnings else "warning",
        "validation_warnings": warnings,
        "validation_warning_count": len(warnings),
    }


def _build_asr_test_endpoint(endpoint: str) -> str:
    normalized = str(endpoint or "").strip().rstrip("/")
    if not normalized:
        return ""
    if normalized.endswith("/audio/transcriptions"):
        return normalized
    return f"{normalized}/audio/transcriptions"


def _sanitize_asr_test_error(message: str) -> str:
    text = str(message or "").strip()
    if not text:
        return "Unknown error"

    sanitized = text.replace("\n", " ").replace("\r", " ")
    while "  " in sanitized:
        sanitized = sanitized.replace("  ", " ")

    return sanitized[:240]


def _sanitize_endpoint_for_display(endpoint: str) -> str:
    raw = str(endpoint or "").strip()
    if not raw:
        return ""

    try:
        parsed = urlsplit(raw)
    except Exception:
        return raw[:160]

    scheme = parsed.scheme or "http"
    netloc = parsed.netloc
    path = parsed.path or ""
    if not netloc:
        return raw[:160]

    return f"{scheme}://{netloc}{path}"[:160]


def _normalize_asr_filename(value: str) -> str:
    filename = str(value or "").strip()
    return filename[:120] if filename else "test-audio.webm"


def _sanitize_transcription_preview(value: str) -> str:
    text = str(value or "").replace("\n", " ").replace("\r", " ").strip()
    while "  " in text:
        text = text.replace("  ", " ")
    return text[:240]


def _resolve_active_profile_name(data):
    asr_section = _get_dict(data, "ASR")
    runtime = _get_dict(data, "runtime")
    selected_module = _get_dict(data, "selected_module")

    candidates = [
        str(runtime.get("asr_profile", "") or "").strip(),
        str(selected_module.get("asr", "") or "").strip(),
        str(selected_module.get("ASR", "") or "").strip(),
    ]

    for candidate in candidates:
        if candidate and isinstance(asr_section.get(candidate), dict):
            return candidate

    for profile_name, block in asr_section.items():
        if isinstance(block, dict):
            return str(profile_name)

    return ""


def _build_profile_summary(profile_name, block, active_profile_name):
    block = block if isinstance(block, dict) else {}
    endpoint = _get_endpoint(block)
    model = _get_model(block)
    api_key = str(block.get("api_key", "") or "").strip()
    validation = _validate_asr_profile(block)

    return {
        "profile_name": str(profile_name or "").strip(),
        "provider": _guess_provider(profile_name, block),
        "type": str(block.get("type", "") or "").strip(),
        "endpoint": endpoint,
        "endpoint_field": _get_endpoint_field_name(block),
        "model": model,
        "has_api_key": bool(api_key),
        "requires_api_key": _asr_requires_api_key(endpoint),
        "output_dir": str(block.get("output_dir", "") or "").strip(),
        "is_active": str(profile_name) == active_profile_name,
        "validation_status": validation["validation_status"],
        "validation_warnings": validation["validation_warnings"],
        "validation_warning_count": validation["validation_warning_count"],
    }


def _build_form_data(summary):
    return {
        "profile_name": summary.get("profile_name", ""),
        "type": summary.get("type", "") or "openai",
        "endpoint": summary.get("endpoint", ""),
        "model": summary.get("model", ""),
        "has_api_key": summary.get("has_api_key", False),
        "requires_api_key": summary.get("requires_api_key", False),
        "output_dir": summary.get("output_dir", ""),
        "is_active": summary.get("is_active", False),
        "validation_status": summary.get("validation_status", "ok"),
        "validation_warnings": summary.get("validation_warnings", []),
        "validation_warning_count": summary.get("validation_warning_count", 0),
    }


def _default_selected_profile():
    preset = ASR_PRESETS["groq"]
    return {
        "profile_name": "",
        "type": preset["type"],
        "endpoint": preset["endpoint"],
        "model": preset["model"],
        "has_api_key": bool(preset["api_key"]),
        "requires_api_key": _asr_requires_api_key(preset["endpoint"]),
        "output_dir": preset["output_dir"],
        "is_active": False,
        "validation_status": "ok",
        "validation_warnings": [],
        "validation_warning_count": 0,
    }


def get_all_asr_configs():
    data = _safe_load_config_data()
    asr_section = _get_dict(data, "ASR")
    active_profile_name = _resolve_active_profile_name(data)
    profiles = {}

    for profile_name, block in asr_section.items():
        if isinstance(block, dict):
            profiles[str(profile_name)] = _build_profile_summary(
                profile_name=str(profile_name),
                block=block,
                active_profile_name=active_profile_name,
            )

    return profiles


def get_active_asr():
    data = _safe_load_config_data()
    active_profile_name = _resolve_active_profile_name(data)
    asr_section = _get_dict(data, "ASR")
    block = asr_section.get(active_profile_name, {})
    if not isinstance(block, dict):
        block = {}

    return _build_profile_summary(active_profile_name, block, active_profile_name)


def test_active_asr(audio_bytes: bytes, filename: str, content_type: str = "") -> dict:
    active = get_active_asr()
    profile_name = str(active.get("profile_name", "") or "").strip()
    endpoint = _build_asr_test_endpoint(active.get("endpoint", ""))
    model = str(active.get("model", "") or "").strip()
    api_key = ""

    data = _safe_load_config_data()
    asr_section = _get_dict(data, "ASR")
    active_block = asr_section.get(profile_name, {})
    if isinstance(active_block, dict):
        api_key = str(active_block.get("api_key", "") or "").strip()

    validation_status = active.get("validation_status", "ok")
    validation_warnings = active.get("validation_warnings", [])
    validation_warning_count = active.get("validation_warning_count", 0)
    safe_filename = _normalize_asr_filename(filename)

    result = {
        "action_kind": "asr_test",
        "selected_profile_name": profile_name,
        "endpoint": _sanitize_endpoint_for_display(endpoint),
        "validation_status": validation_status,
        "validation_warnings": validation_warnings,
        "validation_warning_count": validation_warning_count,
        "test_filename": safe_filename,
        "logs_href": "/logs?source=xserver&lines=200",
        "logs_label": "View Xiaozhi logs",
    }

    if not profile_name:
        result["ok"] = False
        result["message"] = "No active ASR profile to test"
        result["error_reason"] = "runtime.asr_profile not resolved"
        return result

    if not endpoint:
        result["ok"] = False
        result["message"] = f"ASR test not run: {profile_name}"
        result["error_reason"] = "audio/transcriptions endpoint unavailable"
        return result

    if not audio_bytes:
        result["ok"] = False
        result["message"] = f"ASR test not run: {profile_name}"
        result["error_reason"] = "No audio file uploaded"
        return result

    headers = {}
    if api_key and not _api_key_is_intentionally_not_needed(api_key):
        headers["Authorization"] = f"Bearer {api_key}"

    files = {
        "file": (
            safe_filename,
            audio_bytes,
            str(content_type or "").strip() or "application/octet-stream",
        )
    }
    data_payload = {
        "model": model,
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(endpoint, headers=headers, data=data_payload, files=files)
        result["http_status"] = response.status_code

        if response.is_success:
            transcription_text = ""
            try:
                payload = response.json()
            except ValueError:
                payload = {}

            if isinstance(payload, dict):
                transcription_text = str(payload.get("text", "") or "").strip()

            if not transcription_text:
                transcription_text = str(response.text or "").strip()

            result["ok"] = True
            result["message"] = f"ASR test completed: {profile_name}"
            result["transcription_preview"] = _sanitize_transcription_preview(transcription_text)
            return result

        result["ok"] = False
        result["message"] = f"ASR test failed: {profile_name}"

        error_reason = ""
        try:
            payload = response.json()
        except ValueError:
            payload = {}

        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict):
                error_reason = str(error.get("message", "") or "").strip()
            elif error:
                error_reason = str(error).strip()

        if not error_reason:
            error_reason = f"HTTP {response.status_code}"

        result["error_reason"] = _sanitize_asr_test_error(error_reason)
        return result
    except Exception as exc:
        result["ok"] = False
        result["message"] = f"ASR test failed: {profile_name}"
        result["error_reason"] = _sanitize_asr_test_error(str(exc))
        return result


def get_asr_page_data(selected_profile_name=""):
    data = _safe_load_config_data()
    profiles_by_name = get_all_asr_configs()
    active = get_active_asr()
    active_profile_name = active.get("profile_name", "")

    selected_name = str(selected_profile_name or "").strip()
    if selected_name and selected_name in profiles_by_name:
        selected = profiles_by_name[selected_name]
    elif active_profile_name and active_profile_name in profiles_by_name:
        selected = profiles_by_name[active_profile_name]
    elif profiles_by_name:
        selected = next(iter(profiles_by_name.values()))
    else:
        selected = _default_selected_profile()

    runtime = _get_dict(data, "runtime")
    selected_module = _get_dict(data, "selected_module")

    return {
        "presets": ASR_PRESETS,
        "profiles": sorted(
            profiles_by_name.values(),
            key=lambda profile: (
                0 if profile.get("is_active") else 1,
                str(profile.get("profile_name", "")).lower(),
            ),
        ),
        "active": active,
        "selected": _build_form_data(selected),
        "runtime_asr_profile": str(runtime.get("asr_profile", "") or "").strip(),
        "legacy_selected_module_name": str(selected_module.get("asr", "") or "").strip(),
        "logical_selected_module_name": str(selected_module.get("ASR", "") or "").strip(),
    }


def update_single_asr_profile(profile_name, patch):
    profile_name = _sanitize_profile_name(profile_name)
    if not profile_name:
        return {"ok": False, "message": "Invalid profile name"}
    if not _is_valid_profile_name(profile_name):
        return _profile_name_error(profile_name)

    data, load_error = _load_config_data_for_update()
    if load_error:
        return {"ok": False, "message": load_error}

    asr_section = _ensure_dict(data, "ASR")
    existing_block = asr_section.get(profile_name)
    if not isinstance(existing_block, dict):
        return {"ok": False, "message": f"Profile does not exist: {profile_name}"}

    type_value = str(patch.get("type", existing_block.get("type", "")) or "").strip()
    endpoint = str(patch.get("endpoint", _get_endpoint(existing_block)) or "").strip()
    model = str(patch.get("model", _get_model(existing_block)) or "").strip()
    output_dir = str(patch.get("output_dir", existing_block.get("output_dir", "")) or "").strip()
    api_key_input = str(patch.get("api_key", "") or "").strip()

    final_api_key = str(existing_block.get("api_key", "") or "").strip()
    if api_key_input:
        final_api_key = api_key_input

    if not type_value:
        return {"ok": False, "message": "The type field cannot be empty"}
    if not endpoint:
        return {"ok": False, "message": "The API URL / Base URL field cannot be empty"}
    if not model:
        return {"ok": False, "message": "The model field cannot be empty"}
    if _asr_requires_api_key(endpoint) and not final_api_key:
        return {"ok": False, "message": "Missing API key when required"}

    updated_block = dict(existing_block)
    endpoint_field = _get_endpoint_field_name(existing_block)
    updated_block["type"] = type_value
    updated_block["model"] = model
    updated_block["api_key"] = final_api_key
    updated_block.pop("model_name", None)

    if endpoint_field == "api_url":
        updated_block["api_url"] = endpoint
        updated_block.pop("base_url", None)
    else:
        updated_block["base_url"] = endpoint
        updated_block.pop("api_url", None)

    if output_dir:
        updated_block["output_dir"] = output_dir
    else:
        updated_block.pop("output_dir", None)

    asr_section[profile_name] = updated_block

    new_yaml = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    result = save_config(new_yaml)
    if result.get("ok"):
        result["message"] = f"Profile updated: {profile_name}"
        result["selected_profile_name"] = profile_name

    return result


def set_active_asr(profile_name):
    profile_name = _sanitize_profile_name(profile_name)
    if not profile_name:
        return {"ok": False, "message": "Invalid ASR profile"}
    if not _is_valid_profile_name(profile_name):
        return _profile_name_error(profile_name)

    data, load_error = _load_config_data_for_update()
    if load_error:
        return {"ok": False, "message": load_error}

    asr_section = _get_dict(data, "ASR")
    if not isinstance(asr_section.get(profile_name), dict):
        return {"ok": False, "message": f"Profile does not exist: {profile_name}"}

    runtime = _ensure_dict(data, "runtime")
    runtime["asr_profile"] = profile_name

    selected_module = data.get("selected_module")
    if isinstance(selected_module, dict) and "asr" in selected_module:
        selected_module["asr"] = profile_name

    new_yaml = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    result = save_config(new_yaml)
    if result.get("ok"):
        summary = _build_profile_summary(profile_name, asr_section.get(profile_name, {}), profile_name)
        result["message"] = f"Active profile changed: {profile_name}"
        result["selected_profile_name"] = profile_name
        result["validation_status"] = summary.get("validation_status", "ok")
        result["validation_warnings"] = summary.get("validation_warnings", [])
        result["validation_warning_count"] = summary.get("validation_warning_count", 0)

    return result


def _next_profile_name(asr_section, base_name):
    final_name = base_name
    counter = 2
    while final_name in asr_section:
        final_name = f"{base_name}_{counter}"
        counter += 1
    return final_name


def create_asr_profile(provider_id, profile_name=None):
    provider_id = str(provider_id or "").strip()
    if provider_id not in ASR_PRESETS:
        return {"ok": False, "message": f"Unsupported ASR preset: {provider_id}"}

    requested_profile_name = _sanitize_profile_name(profile_name or "")
    if requested_profile_name and not _is_valid_profile_name(requested_profile_name):
        return _profile_name_error(requested_profile_name)

    data, load_error = _load_config_data_for_update()
    if load_error:
        return {"ok": False, "message": load_error}

    asr_section = _ensure_dict(data, "ASR")
    preset = ASR_PRESETS[provider_id]
    base_name = requested_profile_name or provider_id
    if not _is_valid_profile_name(base_name):
        return _profile_name_error(base_name)

    if requested_profile_name and requested_profile_name in asr_section:
        return {"ok": False, "message": f"Profile already exists: {requested_profile_name}"}

    final_profile_name = requested_profile_name or _next_profile_name(asr_section, base_name)
    new_block = {
        "type": preset["type"],
        preset["endpoint_field"]: preset["endpoint"],
        "model": preset["model"],
        "api_key": preset["api_key"],
    }
    if preset.get("output_dir"):
        new_block["output_dir"] = preset["output_dir"]

    asr_section[final_profile_name] = new_block

    new_yaml = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    result = save_config(new_yaml)
    if result.get("ok"):
        result["message"] = f"Profile created: {final_profile_name}"
        result["selected_profile_name"] = final_profile_name

    return result


def delete_asr_profile(profile_name):
    profile_name = _sanitize_profile_name(profile_name)
    if not profile_name:
        return {"ok": False, "message": "Invalid profile name"}
    if not _is_valid_profile_name(profile_name):
        return _profile_name_error(profile_name)

    data, load_error = _load_config_data_for_update()
    if load_error:
        return {"ok": False, "message": load_error}

    asr_section = _get_dict(data, "ASR")
    if not isinstance(asr_section.get(profile_name), dict):
        return {"ok": False, "message": f"Profile does not exist: {profile_name}"}

    active_profile_name = _resolve_active_profile_name(data)
    if profile_name == active_profile_name:
        return {"ok": False, "message": f"Active profile cannot be deleted: {profile_name}"}

    del asr_section[profile_name]
    data["ASR"] = asr_section

    new_yaml = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    result = save_config(new_yaml)
    if result.get("ok"):
        result["message"] = f"Profile deleted: {profile_name}"
        result["selected_profile_name"] = active_profile_name

    return result
