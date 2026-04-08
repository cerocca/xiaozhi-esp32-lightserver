from copy import deepcopy
from typing import Any, Dict


PROFILE_KEY_MAP = {
    "LLM": "llm_profile",
    "ASR": "asr_profile",
    "TTS": "tts_profile",
}

LEGACY_SELECTED_MODULE_KEY_MAP = {
    "LLM": "llm",
    "ASR": "asr",
    "TTS": "tts",
}


def _resolve_runtime_profile(
    runtime: Dict[str, Any], selected_module: Dict[str, Any], runtime_key: str, legacy_key: str
) -> Any:
    # Preferred normalized source is runtime.*_profile. Lowercase selected_module keys
    # remain accepted only as legacy compatibility inputs when runtime is unset.
    if runtime_key in runtime:
        return runtime.get(runtime_key)
    return selected_module.get(legacy_key)


def get_runtime_profile(config: Dict[str, Any], kind: str) -> Any:
    runtime = config.get("runtime", {})
    profile_key = PROFILE_KEY_MAP.get(kind)
    if not isinstance(runtime, dict) or profile_key is None:
        return None
    return runtime.get(profile_key)


def get_selected_module_name(config: Dict[str, Any], kind: str) -> Any:
    selected_module = config.get("selected_module", {})
    if not isinstance(selected_module, dict):
        return None
    return selected_module.get(kind)


def validate_runtime_profile(config: Dict[str, Any], kind: str) -> Dict[str, Any]:
    profile_configs = config.get(kind, {})
    if not isinstance(profile_configs, dict):
        profile_configs = {}

    runtime_profile = get_runtime_profile(config, kind)
    logical_module_name = get_selected_module_name(config, kind)
    has_runtime_profile = runtime_profile not in (None, "")
    is_valid = has_runtime_profile and runtime_profile in profile_configs

    return {
        "kind": kind,
        "selected_profile": runtime_profile,
        "logical_module": logical_module_name,
        "profile_valid": is_valid,
        "using_fallback_base_config": not is_valid,
        "available_profiles": tuple(profile_configs.keys()),
    }


def _add_model_alias(config: Any) -> Dict[str, Any]:
    if not isinstance(config, dict):
        return {}

    normalized_config = dict(config)
    if "model_name" in normalized_config and "model" not in normalized_config:
        normalized_config["model"] = normalized_config["model_name"]
    if "model" in normalized_config and "model_name" not in normalized_config:
        normalized_config["model_name"] = normalized_config["model"]
    return normalized_config


def _copy_model_name_to_model(providers: Any) -> None:
    if not isinstance(providers, dict):
        return

    for provider_config in providers.values():
        if isinstance(provider_config, dict):
            provider_config.update(_add_model_alias(provider_config))


def normalize_config(raw_config: dict) -> Dict[str, Any]:
    """Normalize config to the target profile-aware YAML shape.

    Preferred structure:
    - LLM / ASR / TTS: maps of named provider profiles
    - runtime.*_profile: active provider profile to resolve at runtime
    - selected_module uppercase keys: logical module or driver selection

    Backward compatibility:
    - selected_module.llm / asr / tts are still accepted as legacy inputs
    - legacy keys are preserved in the returned config and are not rewritten
    """
    config = deepcopy(raw_config) if isinstance(raw_config, dict) else {}

    runtime = config.get("runtime")
    if not isinstance(runtime, dict):
        runtime = {}
    else:
        runtime = dict(runtime)

    selected_module = config.get("selected_module")
    if not isinstance(selected_module, dict):
        selected_module = {}
    else:
        selected_module = dict(selected_module)

    # Uppercase selected_module keys continue to represent the logical module
    # or driver selection. runtime.*_profile is the preferred source of truth
    # for choosing the active provider profile inside LLM / ASR / TTS maps.
    # Lowercase selected_module keys remain legacy compatibility inputs only.
    for kind, runtime_key in PROFILE_KEY_MAP.items():
        legacy_key = LEGACY_SELECTED_MODULE_KEY_MAP[kind]
        runtime[runtime_key] = _resolve_runtime_profile(
            runtime, selected_module, runtime_key, legacy_key
        )

    config["runtime"] = runtime
    config["selected_module"] = selected_module

    for module_name in ("LLM", "ASR", "TTS"):
        _copy_model_name_to_model(config.get(module_name))

    return config


def _resolve_profile_config(config: dict, kind: str) -> Dict[str, Any]:
    profile_configs = config.get(kind, {})
    if not isinstance(profile_configs, dict):
        return {}

    logical_module_name = get_selected_module_name(config, kind)
    base_cfg = profile_configs.get(logical_module_name, {})
    if not isinstance(base_cfg, dict):
        base_cfg = {}

    validation = validate_runtime_profile(config, kind)
    runtime_profile = validation["selected_profile"]
    if validation["profile_valid"]:
        final_cfg = dict(base_cfg)
        final_cfg.update(profile_configs[runtime_profile])
    else:
        final_cfg = dict(base_cfg)

    return _add_model_alias(final_cfg)


def resolve_llm_config(config: dict) -> Dict[str, Any]:
    return _resolve_profile_config(config, "LLM")


def resolve_asr_config(config: dict) -> Dict[str, Any]:
    return _resolve_profile_config(config, "ASR")


def resolve_tts_config(config: dict) -> Dict[str, Any]:
    return _resolve_profile_config(config, "TTS")
