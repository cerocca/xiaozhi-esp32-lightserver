import yaml
import re

from app.services.config_service import read_config_text, save_config


PROVIDER_PRESETS = {
    "groq": {
        "module_name": "groq_llm",
        "type": "openai",
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.1-8b-instant",
        "default_api_key": "",
        "default_temperature": 0.7,
        "models": [
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
        ],
    },
    "openai": {
        "module_name": "openai_llm",
        "type": "openai",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "default_api_key": "",
        "default_temperature": 0.7,
        "models": [
            "gpt-4o-mini",
            "gpt-4.1-mini",
        ],
    },
    "ollama": {
        "module_name": "ollama_llm",
        "type": "openai",
        "base_url": "http://192.168.1.69:11434/v1",
        "default_model": "llama3.1:8b",
        "default_api_key": "not-needed",
        "default_temperature": 0.7,
        "models": [
            "llama3.1:8b",
            "qwen2.5:7b",
        ],
    },
    "anthropic": {
        "module_name": "anthropic_llm",
        "type": "openai",
        "base_url": "https://api.anthropic.com/v1/",
        "default_model": "claude-sonnet-4-20250514",
        "default_api_key": "",
        "default_temperature": 0.7,
        "models": [
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
        ],
    },
}


def get_provider_presets() -> dict:
    return PROVIDER_PRESETS


def _sanitize_profile_name(value: str) -> str:
    return str(value or "").strip()


PROFILE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _is_valid_profile_name(value: str) -> bool:
    return bool(PROFILE_NAME_PATTERN.fullmatch(str(value or "").strip()))


def _get_profile_name_validation_error(profile_name: str) -> dict:
    return {
        "ok": False,
        "message": (
            f"Nome profilo non valido: {profile_name}. "
            "Usa solo lettere, numeri, underscore (_) o trattino (-)."
        ),
    }


def normalize_llm_form_data(
    provider: str,
    api_key: str,
    model: str,
    base_url: str,
    temperature: float,
) -> dict:
    return {
        "provider": str(provider or "").strip(),
        "api_key": str(api_key or "").strip(),
        "model": str(model or "").strip(),
        "base_url": str(base_url or "").strip(),
        "temperature": max(0.0, min(2.0, float(temperature))),
    }


def _safe_load_config_data() -> dict:
    try:
        content = read_config_text()
        data = yaml.safe_load(content) or {}
    except (OSError, yaml.YAMLError):
        return {}

    if not isinstance(data, dict):
        return {}
    return data


def _load_config_data_for_update() -> tuple[dict | None, str]:
    try:
        content = read_config_text()
    except OSError as e:
        return None, f"Impossibile leggere la config corrente: {e}"

    try:
        data = yaml.safe_load(content) or {}
    except yaml.YAMLError as e:
        return None, f"Config corrente non valida: {e}"

    if not isinstance(data, dict):
        return None, "Config corrente non valida: la root YAML deve essere una mappa"

    return data, ""


def _get_dict(data: dict, key: str) -> dict:
    value = data.get(key, {})
    if isinstance(value, dict):
        return value
    return {}


def _ensure_dict(data: dict, key: str) -> dict:
    value = data.get(key)
    if isinstance(value, dict):
        return value
    data[key] = {}
    return data[key]


def _provider_from_module_name(module_name: str) -> str:
    if module_name in PROVIDER_PRESETS:
        return module_name

    for provider_name, preset in PROVIDER_PRESETS.items():
        if preset["module_name"] == module_name:
            return provider_name

    return ""


def _guess_provider(module_name: str, block: dict) -> str:
    provider_name = _provider_from_module_name(module_name)
    if provider_name:
        return provider_name

    if not isinstance(block, dict):
        block = {}

    block_base_url = str(block.get("base_url", "")).strip().rstrip("/")
    for preset_provider, preset in PROVIDER_PRESETS.items():
        preset_base_url = str(preset.get("base_url", "")).strip().rstrip("/")
        if block_base_url and block_base_url == preset_base_url:
            return preset_provider

    if "groq" in PROVIDER_PRESETS:
        return "groq"
    return next(iter(PROVIDER_PRESETS), "")


def _get_llm_profile_names(data: dict) -> tuple[str, str]:
    runtime = _get_dict(data, "runtime")
    selected_module = _get_dict(data, "selected_module")

    runtime_llm_profile = str(runtime.get("llm_profile", "") or "").strip()
    legacy_module_name = str(selected_module.get("llm", "") or "").strip()

    return runtime_llm_profile, legacy_module_name


def _get_existing_llm_block(data: dict, *names: str) -> tuple[str, dict]:
    llm_section = _get_dict(data, "LLM")

    for name in names:
        if name and isinstance(llm_section.get(name), dict):
            return name, llm_section[name]

    return "", {}


def _profile_has_api_key(value) -> bool:
    return bool(str(value or "").strip())


def _provider_requires_api_key(provider_id: str) -> bool:
    return provider_id in {"groq", "openai", "anthropic"}


def _get_block_model(block: dict) -> str:
    if not isinstance(block, dict):
        return ""

    model = str(block.get("model", "") or "").strip()
    if model:
        return model

    return str(block.get("model_name", "") or "").strip()


def _normalize_llm_block_for_write(block: dict, model: str) -> dict:
    normalized_block = dict(block) if isinstance(block, dict) else {}
    normalized_model = str(model or "").strip()

    if normalized_model:
        normalized_block["model"] = normalized_model

    legacy_model_name = str(normalized_block.get("model_name", "") or "").strip()
    if legacy_model_name and legacy_model_name != normalized_block.get("model", ""):
        return normalized_block

    normalized_block.pop("model_name", None)
    return normalized_block


def _is_legacy_profile(profile_name: str, provider_id: str) -> bool:
    profile_name = str(profile_name or "").strip()
    provider_id = str(provider_id or "").strip()
    if not profile_name:
        return False

    if profile_name in PROVIDER_PRESETS:
        return False

    preset = PROVIDER_PRESETS.get(provider_id, {})
    expected_name = str(preset.get("module_name", "") or "").strip()
    if expected_name and profile_name == expected_name:
        return False

    return any(ch.isupper() for ch in profile_name)


def _build_profile_summary(profile_name: str, block: dict, active_profile_name: str) -> dict:
    block = block if isinstance(block, dict) else {}
    provider_id = _guess_provider(profile_name, block) if profile_name or block else ""
    has_api_key = _profile_has_api_key(block.get("api_key"))
    is_legacy = _is_legacy_profile(profile_name, provider_id)

    return {
        "profile_name": profile_name,
        "provider_id": provider_id,
        "type": str(block.get("type", "") or "").strip(),
        "base_url": str(block.get("base_url", "") or "").strip(),
        "model": _get_block_model(block),
        "temperature": block.get("temperature", PROVIDER_PRESETS.get(provider_id, {}).get("default_temperature", 0.7)),
        "api_key": str(block.get("api_key", "") or "").strip(),
        "has_api_key": has_api_key,
        "requires_api_key": _provider_requires_api_key(provider_id),
        "api_key_status": "present" if has_api_key else "missing",
        "is_active": profile_name == active_profile_name,
        "is_legacy": is_legacy,
        "legacy_note": (
            "Profilo legacy, consigliato creare un nuovo profilo."
            if is_legacy else ""
        ),
        "raw_block": block,
    }


def _resolve_active_profile_name(data: dict) -> str:
    runtime_llm_profile, legacy_module_name = _get_llm_profile_names(data)
    llm_section = _get_dict(data, "LLM")

    if runtime_llm_profile and isinstance(llm_section.get(runtime_llm_profile), dict):
        return runtime_llm_profile

    if legacy_module_name and isinstance(llm_section.get(legacy_module_name), dict):
        return legacy_module_name

    if runtime_llm_profile:
        return runtime_llm_profile

    if legacy_module_name:
        return legacy_module_name

    for profile_name, block in llm_section.items():
        if isinstance(block, dict):
            return profile_name

    return ""


def _build_profile_form_data(summary: dict) -> dict:
    provider_id = summary.get("provider_id", "")
    preset = PROVIDER_PRESETS.get(provider_id, {})

    return {
        "profile_name": summary.get("profile_name", ""),
        "provider_id": provider_id,
        "api_key": "",
        "has_api_key": summary.get("has_api_key", False),
        "model": summary.get("model", "") or preset.get("default_model", ""),
        "base_url": summary.get("base_url", "") or preset.get("base_url", ""),
        "temperature": summary.get("temperature", preset.get("default_temperature", 0.7)),
        "is_active": summary.get("is_active", False),
        "requires_api_key": summary.get("requires_api_key", _provider_requires_api_key(provider_id)),
        "is_legacy": summary.get("is_legacy", False),
        "legacy_note": summary.get("legacy_note", ""),
    }


def _build_llm_page_data(selected_profile_name: str = "") -> dict:
    presets = get_provider_presets()
    profiles = get_all_llm_configs()
    active = get_active_llm()
    current = get_current_llm_config()
    active_profile_name = active.get("profile_name", "")

    if selected_profile_name and selected_profile_name in profiles:
        selected = profiles[selected_profile_name]
    elif active_profile_name and active_profile_name in profiles:
        selected = profiles[active_profile_name]
    elif profiles:
        selected = next(iter(profiles.values()))
    else:
        default_provider_id = "groq" if "groq" in presets else next(iter(presets), "")
        selected = {
            "profile_name": "",
            "provider_id": default_provider_id,
            "model": presets.get(default_provider_id, {}).get("default_model", ""),
            "base_url": presets.get(default_provider_id, {}).get("base_url", ""),
            "temperature": presets.get(default_provider_id, {}).get("default_temperature", 0.7),
            "has_api_key": False,
            "is_active": False,
        }

    return {
        "presets": presets,
        "profiles": sorted(
            profiles.values(),
            key=lambda profile: (
                0 if profile.get("is_active") else 1,
                str(profile.get("profile_name", "")).lower(),
            ),
        ),
        "profiles_by_name": profiles,
        "active": active,
        "selected": _build_profile_form_data(selected),
        "runtime_llm_profile": current.get("runtime_llm_profile", ""),
        "legacy_selected_module_name": current.get("legacy_selected_module_name", ""),
    }


def get_all_llm_configs() -> dict[str, dict]:
    data = _safe_load_config_data()
    llm_section = _get_dict(data, "LLM")
    active_profile_name = _resolve_active_profile_name(data)
    profiles = {}

    for profile_name, block in llm_section.items():
        if not isinstance(block, dict):
            continue
        profiles[profile_name] = _build_profile_summary(profile_name, block, active_profile_name)

    return profiles


def get_active_llm() -> dict:
    data = _safe_load_config_data()
    active_profile_name = _resolve_active_profile_name(data)
    llm_section = _get_dict(data, "LLM")
    block = llm_section.get(active_profile_name, {})

    if not isinstance(block, dict):
        block = {}

    return _build_profile_summary(active_profile_name, block, active_profile_name)


def get_llm_page_data(selected_profile_name: str = "") -> dict:
    return _build_llm_page_data(selected_profile_name=selected_profile_name)


def get_current_llm_config() -> dict:
    active = get_active_llm()
    data = _safe_load_config_data()
    runtime_llm_profile, legacy_module_name = _get_llm_profile_names(data)

    return {
        "selected_module_name": active.get("profile_name", ""),
        "selected_block": active.get("raw_block", {}),
        "provider_guess": active.get("provider_id", ""),
        "runtime_llm_profile": runtime_llm_profile,
        "legacy_selected_module_name": legacy_module_name,
        "raw_config": data,
    }


def get_llm_form_data() -> dict:
    page_data = get_llm_page_data()
    selected = page_data.get("selected", {})
    active = page_data.get("active", {})

    return {
        "presets": page_data.get("presets", {}),
        "provider": selected.get("provider_id", ""),
        "api_key": selected.get("api_key", ""),
        "model": selected.get("model", ""),
        "base_url": selected.get("base_url", ""),
        "temperature": selected.get("temperature", 0.7),
        "selected_module_name": selected.get("profile_name", ""),
        "active_provider": active.get("provider_id", ""),
        "active_model": active.get("model", ""),
        "active_selected_module_name": active.get("profile_name", ""),
    }


def validate_llm_input(provider: str, api_key: str, model: str, base_url: str) -> dict:
    if provider not in PROVIDER_PRESETS:
        return {"ok": False, "message": f"Provider non supportato: {provider}"}

    if not model.strip():
        return {"ok": False, "message": "Il model non può essere vuoto"}

    if not base_url.strip():
        return {"ok": False, "message": "La base URL non può essere vuota"}

    if provider in {"groq", "openai", "anthropic"} and not api_key.strip():
        # Non errore bloccante se la chiave esiste già in config; questo viene gestito dopo.
        return {"ok": True, "message": "ok"}

    return {"ok": True, "message": "ok"}


def set_active_llm(profile_name: str) -> dict:
    profile_name = _sanitize_profile_name(profile_name)
    if not profile_name:
        return {"ok": False, "message": "Profilo LLM non valido"}
    if not _is_valid_profile_name(profile_name):
        return _get_profile_name_validation_error(profile_name)

    data, load_error = _load_config_data_for_update()
    if load_error:
        return {"ok": False, "message": load_error}

    llm_section = _get_dict(data, "LLM")
    if not isinstance(llm_section.get(profile_name), dict):
        return {"ok": False, "message": f"Profilo inesistente: {profile_name}"}

    runtime = _ensure_dict(data, "runtime")
    runtime["llm_profile"] = profile_name

    selected_module = data.get("selected_module")
    if isinstance(selected_module, dict):
        selected_module["llm"] = profile_name

    new_yaml = yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
    )

    result = save_config(new_yaml)
    if result.get("ok"):
        active = _build_profile_summary(profile_name, llm_section.get(profile_name, {}), profile_name)
        result["message"] = f"Profilo attivo cambiato: {profile_name}"
        result["selected_module_name"] = profile_name
        result["runtime_llm_profile"] = profile_name
        result["legacy_selected_module_name"] = (
            profile_name if isinstance(data.get("selected_module"), dict) else ""
        )
        result["provider"] = active.get("provider_id", "")
        result["active_model"] = active.get("model", "")
        result["active_base_url"] = active.get("base_url", "")

    return result


def update_single_provider(
    profile_name: str,
    provider_id: str,
    patch: dict,
    activate: bool = False,
) -> dict:
    profile_name = _sanitize_profile_name(profile_name)
    provider_id = str(provider_id or "").strip()

    if not profile_name:
        return {"ok": False, "message": "Nome profilo non valido"}
    if not _is_valid_profile_name(profile_name):
        return _get_profile_name_validation_error(profile_name)

    if provider_id not in PROVIDER_PRESETS:
        return {"ok": False, "message": f"Provider non supportato: {provider_id}"}

    normalized = normalize_llm_form_data(
        provider_id,
        patch.get("api_key", ""),
        patch.get("model", ""),
        patch.get("base_url", ""),
        patch.get("temperature", PROVIDER_PRESETS[provider_id].get("default_temperature", 0.7)),
    )

    validation = validate_llm_input(
        normalized["provider"],
        normalized["api_key"],
        normalized["model"],
        normalized["base_url"],
    )
    if not validation["ok"]:
        return validation

    data, load_error = _load_config_data_for_update()
    if load_error:
        return {"ok": False, "message": load_error}

    llm_section = _ensure_dict(data, "LLM")
    existing_block = llm_section.get(profile_name, {})
    if not isinstance(existing_block, dict):
        existing_block = {}

    final_api_key = str(existing_block.get("api_key", "") or "").strip()
    if normalized["api_key"]:
        final_api_key = normalized["api_key"]

    if provider_id in {"groq", "openai", "anthropic"} and not final_api_key:
        return {
            "ok": False,
            "message": f"API key mancante: il provider {provider_id} richiede una chiave.",
        }

    preset = PROVIDER_PRESETS[provider_id]
    updated_block = {}
    updated_block.update(existing_block)
    updated_block.update(
        {
            "type": preset["type"],
            "base_url": normalized["base_url"],
            "api_key": final_api_key,
            "model": normalized["model"],
            "temperature": normalized["temperature"],
        }
    )
    updated_block = _normalize_llm_block_for_write(updated_block, normalized["model"])

    llm_section[profile_name] = updated_block

    if activate:
        runtime = _ensure_dict(data, "runtime")
        runtime["llm_profile"] = profile_name

        selected_module = data.get("selected_module")
        if isinstance(selected_module, dict):
            selected_module["llm"] = profile_name

    new_yaml = yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
    )

    result = save_config(new_yaml)
    if result.get("ok"):
        active_profile_name = _resolve_active_profile_name(data)
        summary = _build_profile_summary(profile_name, updated_block, active_profile_name)
        result["message"] = f"Profilo aggiornato: {profile_name}"
        result["selected_module_name"] = profile_name
        result["provider"] = provider_id
        result["active_model"] = summary.get("model", "")
        result["active_base_url"] = summary.get("base_url", "")
        result["runtime_llm_profile"] = _get_dict(data, "runtime").get("llm_profile", "")
        result["legacy_selected_module_name"] = _get_dict(data, "selected_module").get("llm", "")

    return result


def create_provider_profile(provider_id: str, profile_name: str | None = None) -> dict:
    provider_id = str(provider_id or "").strip()
    if provider_id not in PROVIDER_PRESETS:
        return {"ok": False, "message": f"Provider non supportato: {provider_id}"}

    preset = PROVIDER_PRESETS[provider_id]
    requested_profile_name = _sanitize_profile_name(profile_name or "")
    if requested_profile_name and not _is_valid_profile_name(requested_profile_name):
        return _get_profile_name_validation_error(requested_profile_name)

    data, load_error = _load_config_data_for_update()
    if load_error:
        return {"ok": False, "message": load_error}

    llm_section = _ensure_dict(data, "LLM")
    base_profile_name = requested_profile_name or preset["module_name"]
    if not _is_valid_profile_name(base_profile_name):
        return _get_profile_name_validation_error(base_profile_name)
    final_profile_name = base_profile_name
    counter = 2

    while final_profile_name in llm_section:
        if requested_profile_name:
            return {"ok": False, "message": f"Profilo già esistente: {final_profile_name}"}
        final_profile_name = f"{base_profile_name}_{counter}"
        counter += 1

    llm_section[final_profile_name] = {
        "type": preset["type"],
        "base_url": preset["base_url"],
        "api_key": preset.get("default_api_key", ""),
        "model": preset["default_model"],
        "temperature": preset["default_temperature"],
    }
    llm_section[final_profile_name] = _normalize_llm_block_for_write(
        llm_section[final_profile_name],
        preset["default_model"],
    )

    new_yaml = yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
    )

    result = save_config(new_yaml)
    if result.get("ok"):
        result["selected_module_name"] = final_profile_name
        result["provider"] = provider_id
        result["active_model"] = preset["default_model"]
        result["active_base_url"] = preset["base_url"]

    return result


def delete_provider_profile(profile_name: str) -> dict:
    profile_name = _sanitize_profile_name(profile_name)
    if not profile_name:
        return {"ok": False, "message": "Nome profilo non valido"}
    if not _is_valid_profile_name(profile_name):
        return _get_profile_name_validation_error(profile_name)

    data, load_error = _load_config_data_for_update()
    if load_error:
        return {"ok": False, "message": load_error}

    llm_section = _get_dict(data, "LLM")
    if not isinstance(llm_section.get(profile_name), dict):
        return {"ok": False, "message": f"Profilo inesistente: {profile_name}"}

    active_profile_name = _resolve_active_profile_name(data)
    if profile_name == active_profile_name:
        return {"ok": False, "message": f"Profilo attivo non eliminabile: {profile_name}"}

    del llm_section[profile_name]
    data["LLM"] = llm_section

    new_yaml = yaml.safe_dump(
        data,
        allow_unicode=True,
        sort_keys=False,
    )

    result = save_config(new_yaml)
    if result.get("ok"):
        result["message"] = f"Profilo eliminato: {profile_name}"
        result["deleted_profile_name"] = profile_name
        result["selected_module_name"] = active_profile_name

    return result


def update_llm_config(
    provider: str,
    api_key: str,
    model: str,
    base_url: str,
    temperature: float,
) -> dict:
    preset = PROVIDER_PRESETS.get(provider, {})
    profile_name = preset.get("module_name", "")
    return update_single_provider(
        profile_name=profile_name,
        provider_id=provider,
        patch={
            "api_key": api_key,
            "model": model,
            "base_url": base_url,
            "temperature": temperature,
        },
        activate=True,
    )
