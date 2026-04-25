import re

import yaml

from app.services.config_service import read_config_text, save_config


TTS_PRESETS = {
    "piper_local": {
        "label": "Piper locale",
        "type": "openai",
        "endpoint_field": "api_url",
        "endpoint": "http://127.0.0.1:8091/v1/audio/speech",
        "model": "piper",
        "voice": "riccardo",
        "speed": 1,
        "api_key": "dummy",
        "output_dir": "tmp/",
    },
    "openai_compatible": {
        "label": "OpenAI-compatible",
        "type": "openai",
        "endpoint_field": "api_url",
        "endpoint": "https://example.com/v1/audio/speech",
        "model": "tts-1",
        "voice": "alloy",
        "speed": 1,
        "api_key": "",
        "output_dir": "",
    },
}

TTS_VOICE_OPTIONS = {
    "piper": ["riccardo"],
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
        return None, f"Impossibile leggere la config corrente: {exc}"

    try:
        data = yaml.safe_load(content) or {}
    except yaml.YAMLError as exc:
        return None, f"Config corrente non valida: {exc}"

    if not isinstance(data, dict):
        return None, "Config corrente non valida: la root YAML deve essere una mappa"

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
            f"Nome profilo non valido: {profile_name}. "
            "Usa solo lettere, numeri, underscore (_) o trattino (-)."
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
        return "api_url"

    has_api_url = bool(str(block.get("api_url", "") or "").strip())
    has_base_url = bool(str(block.get("base_url", "") or "").strip())
    if has_base_url and not has_api_url:
        return "base_url"
    return "api_url"


def _normalize_speed(value):
    raw = str(value if value is not None else "").strip()
    if not raw:
        return ""

    try:
        parsed = float(raw)
    except ValueError:
        return raw

    if parsed.is_integer():
        return int(parsed)
    return parsed


def _guess_provider(profile_name, block):
    block = block if isinstance(block, dict) else {}
    model = _get_model(block).lower()
    endpoint = _get_endpoint(block).lower()

    for key in ("provider", "provider_name"):
        value = str(block.get(key, "") or "").strip()
        if value:
            return value

    if model == "piper" or "piper" in endpoint or "8091" in endpoint:
        return "piper"

    type_value = str(block.get("type", "") or "").strip()
    if type_value:
        return type_value

    return str(profile_name or "").strip()


def _is_local_endpoint(endpoint):
    normalized = str(endpoint or "").strip().lower()
    return normalized.startswith("http://127.0.0.1") or normalized.startswith("http://localhost")


def _tts_requires_api_key(endpoint, model):
    normalized_model = str(model or "").strip().lower()
    if normalized_model == "piper":
        return False
    return bool(endpoint) and not _is_local_endpoint(endpoint)


def _resolve_active_profile_name(data):
    tts_section = _get_dict(data, "TTS")
    runtime = _get_dict(data, "runtime")
    selected_module = _get_dict(data, "selected_module")

    candidates = [
        str(runtime.get("tts_profile", "") or "").strip(),
        str(selected_module.get("tts", "") or "").strip(),
        str(selected_module.get("TTS", "") or "").strip(),
    ]

    for candidate in candidates:
        if candidate and isinstance(tts_section.get(candidate), dict):
            return candidate

    for profile_name, block in tts_section.items():
        if isinstance(block, dict):
            return str(profile_name)

    return ""


def _build_profile_summary(profile_name, block, active_profile_name):
    block = block if isinstance(block, dict) else {}
    endpoint = _get_endpoint(block)
    model = _get_model(block)
    api_key = str(block.get("api_key", "") or "").strip()
    provider = _guess_provider(profile_name, block)

    return {
        "profile_name": str(profile_name or "").strip(),
        "provider": provider,
        "type": str(block.get("type", "") or "").strip(),
        "endpoint": endpoint,
        "endpoint_field": _get_endpoint_field_name(block),
        "model": model,
        "voice": str(block.get("voice", "") or "").strip(),
        "speed": _normalize_speed(block.get("speed", "")),
        "has_api_key": bool(api_key),
        "requires_api_key": _tts_requires_api_key(endpoint, model),
        "output_dir": str(block.get("output_dir", "") or "").strip(),
        "is_active": str(profile_name) == active_profile_name,
        "is_local_piper": provider == "piper",
    }


def _build_form_data(summary):
    provider = str(summary.get("provider", "") or "").strip().lower()
    voice_options = list(TTS_VOICE_OPTIONS.get(provider, []))
    current_voice = str(summary.get("voice", "") or "").strip()
    if current_voice and current_voice not in voice_options:
        voice_options.append(current_voice)

    return {
        "profile_name": summary.get("profile_name", ""),
        "provider": provider,
        "type": summary.get("type", "") or "openai",
        "endpoint": summary.get("endpoint", ""),
        "model": summary.get("model", ""),
        "voice": current_voice,
        "voice_options": voice_options,
        "speed": summary.get("speed", ""),
        "has_api_key": summary.get("has_api_key", False),
        "requires_api_key": summary.get("requires_api_key", False),
        "output_dir": summary.get("output_dir", ""),
        "is_active": summary.get("is_active", False),
        "is_local_piper": summary.get("is_local_piper", False),
    }


def _default_selected_profile():
    preset = TTS_PRESETS["piper_local"]
    return {
        "profile_name": "",
        "provider": "piper",
        "type": preset["type"],
        "endpoint": preset["endpoint"],
        "model": preset["model"],
        "voice": preset["voice"],
        "speed": preset["speed"],
        "has_api_key": bool(preset["api_key"]),
        "requires_api_key": _tts_requires_api_key(preset["endpoint"], preset["model"]),
        "output_dir": preset["output_dir"],
        "is_active": False,
        "is_local_piper": True,
    }


def get_all_tts_configs():
    data = _safe_load_config_data()
    tts_section = _get_dict(data, "TTS")
    active_profile_name = _resolve_active_profile_name(data)
    profiles = {}

    for profile_name, block in tts_section.items():
        if isinstance(block, dict):
            profiles[str(profile_name)] = _build_profile_summary(
                profile_name=str(profile_name),
                block=block,
                active_profile_name=active_profile_name,
            )

    return profiles


def get_active_tts():
    data = _safe_load_config_data()
    active_profile_name = _resolve_active_profile_name(data)
    tts_section = _get_dict(data, "TTS")
    block = tts_section.get(active_profile_name, {})
    if not isinstance(block, dict):
        block = {}

    return _build_profile_summary(active_profile_name, block, active_profile_name)


def get_tts_page_data(selected_profile_name=""):
    data = _safe_load_config_data()
    profiles_by_name = get_all_tts_configs()
    active = get_active_tts()
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
        "presets": TTS_PRESETS,
        "profiles": sorted(
            profiles_by_name.values(),
            key=lambda profile: (
                0 if profile.get("is_active") else 1,
                str(profile.get("profile_name", "")).lower(),
            ),
        ),
        "active": active,
        "selected": _build_form_data(selected),
        "runtime_tts_profile": str(runtime.get("tts_profile", "") or "").strip(),
        "legacy_selected_module_name": str(selected_module.get("tts", "") or "").strip(),
        "logical_selected_module_name": str(selected_module.get("TTS", "") or "").strip(),
    }


def update_single_tts_profile(profile_name, patch):
    profile_name = _sanitize_profile_name(profile_name)
    if not profile_name:
        return {"ok": False, "message": "Nome profilo non valido"}
    if not _is_valid_profile_name(profile_name):
        return _profile_name_error(profile_name)

    data, load_error = _load_config_data_for_update()
    if load_error:
        return {"ok": False, "message": load_error}

    tts_section = _ensure_dict(data, "TTS")
    existing_block = tts_section.get(profile_name)
    if not isinstance(existing_block, dict):
        return {"ok": False, "message": f"Profilo inesistente: {profile_name}"}

    type_value = str(patch.get("type", existing_block.get("type", "")) or "").strip()
    endpoint = str(patch.get("endpoint", _get_endpoint(existing_block)) or "").strip()
    model = str(patch.get("model", _get_model(existing_block)) or "").strip()
    voice = str(patch.get("voice", existing_block.get("voice", "")) or "").strip()
    output_dir = str(patch.get("output_dir", existing_block.get("output_dir", "")) or "").strip()
    api_key_input = str(patch.get("api_key", "") or "").strip()
    speed = _normalize_speed(patch.get("speed", existing_block.get("speed", "")))

    final_api_key = str(existing_block.get("api_key", "") or "").strip()
    if api_key_input:
        final_api_key = api_key_input

    if not type_value:
        return {"ok": False, "message": "Il campo type non può essere vuoto"}
    if not endpoint:
        return {"ok": False, "message": "Il campo API URL / Base URL non può essere vuoto"}
    if not model:
        return {"ok": False, "message": "Il campo model non può essere vuoto"}
    if not voice:
        return {"ok": False, "message": "Il campo voice non può essere vuoto"}
    if _tts_requires_api_key(endpoint, model) and not final_api_key:
        return {"ok": False, "message": "API key mancante se necessaria"}

    updated_block = dict(existing_block)
    endpoint_field = _get_endpoint_field_name(existing_block)
    updated_block["type"] = type_value
    updated_block["model"] = model
    updated_block["voice"] = voice
    updated_block["speed"] = speed
    updated_block["api_key"] = final_api_key
    updated_block.pop("model_name", None)

    if endpoint_field == "base_url":
        updated_block["base_url"] = endpoint
        updated_block.pop("api_url", None)
    else:
        updated_block["api_url"] = endpoint
        updated_block.pop("base_url", None)

    if output_dir:
        updated_block["output_dir"] = output_dir
    else:
        updated_block.pop("output_dir", None)

    tts_section[profile_name] = updated_block

    new_yaml = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    result = save_config(new_yaml)
    if result.get("ok"):
        result["message"] = f"Profilo aggiornato: {profile_name}"
        result["selected_profile_name"] = profile_name

    return result


def set_active_tts(profile_name):
    profile_name = _sanitize_profile_name(profile_name)
    if not profile_name:
        return {"ok": False, "message": "Profilo TTS non valido"}
    if not _is_valid_profile_name(profile_name):
        return _profile_name_error(profile_name)

    data, load_error = _load_config_data_for_update()
    if load_error:
        return {"ok": False, "message": load_error}

    tts_section = _get_dict(data, "TTS")
    if not isinstance(tts_section.get(profile_name), dict):
        return {"ok": False, "message": f"Profilo inesistente: {profile_name}"}

    runtime = _ensure_dict(data, "runtime")
    runtime["tts_profile"] = profile_name

    selected_module = data.get("selected_module")
    if isinstance(selected_module, dict) and "tts" in selected_module:
        selected_module["tts"] = profile_name

    new_yaml = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    result = save_config(new_yaml)
    if result.get("ok"):
        result["message"] = f"Profilo attivo cambiato: {profile_name}"
        result["selected_profile_name"] = profile_name

    return result


def _next_profile_name(tts_section, base_name):
    final_name = base_name
    counter = 2
    while final_name in tts_section:
        final_name = f"{base_name}_{counter}"
        counter += 1
    return final_name


def create_tts_profile(provider_id, profile_name=None):
    provider_id = str(provider_id or "").strip()
    if provider_id not in TTS_PRESETS:
        return {"ok": False, "message": f"Preset TTS non supportato: {provider_id}"}

    requested_profile_name = _sanitize_profile_name(profile_name or "")
    if requested_profile_name and not _is_valid_profile_name(requested_profile_name):
        return _profile_name_error(requested_profile_name)

    data, load_error = _load_config_data_for_update()
    if load_error:
        return {"ok": False, "message": load_error}

    tts_section = _ensure_dict(data, "TTS")
    preset = TTS_PRESETS[provider_id]
    base_name = requested_profile_name or provider_id
    if not _is_valid_profile_name(base_name):
        return _profile_name_error(base_name)

    if requested_profile_name and requested_profile_name in tts_section:
        return {"ok": False, "message": f"Profilo già esistente: {requested_profile_name}"}

    final_profile_name = requested_profile_name or _next_profile_name(tts_section, base_name)
    new_block = {
        "type": preset["type"],
        preset["endpoint_field"]: preset["endpoint"],
        "model": preset["model"],
        "voice": preset["voice"],
        "speed": preset["speed"],
        "api_key": preset["api_key"],
    }
    if preset.get("output_dir"):
        new_block["output_dir"] = preset["output_dir"]

    tts_section[final_profile_name] = new_block

    new_yaml = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    result = save_config(new_yaml)
    if result.get("ok"):
        result["message"] = f"Profilo creato: {final_profile_name}"
        result["selected_profile_name"] = final_profile_name

    return result


def delete_tts_profile(profile_name):
    profile_name = _sanitize_profile_name(profile_name)
    if not profile_name:
        return {"ok": False, "message": "Nome profilo non valido"}
    if not _is_valid_profile_name(profile_name):
        return _profile_name_error(profile_name)

    data, load_error = _load_config_data_for_update()
    if load_error:
        return {"ok": False, "message": load_error}

    tts_section = _get_dict(data, "TTS")
    if not isinstance(tts_section.get(profile_name), dict):
        return {"ok": False, "message": f"Profilo inesistente: {profile_name}"}

    active_profile_name = _resolve_active_profile_name(data)
    if profile_name == active_profile_name:
        return {"ok": False, "message": f"Profilo attivo non eliminabile: {profile_name}"}

    del tts_section[profile_name]
    data["TTS"] = tts_section

    new_yaml = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    result = save_config(new_yaml)
    if result.get("ok"):
        result["message"] = f"Profilo eliminato: {profile_name}"
        result["selected_profile_name"] = active_profile_name

    return result
