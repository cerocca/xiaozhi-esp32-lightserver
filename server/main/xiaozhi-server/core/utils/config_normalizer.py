from copy import deepcopy
from typing import Any, Dict


def _add_model_alias(config: Any) -> Dict[str, Any]:
    if not isinstance(config, dict):
        return {}

    normalized_config = dict(config)
    if "model_name" in normalized_config and "model" not in normalized_config:
        normalized_config["model"] = normalized_config["model_name"]
    return normalized_config


def _copy_model_name_to_model(providers: Any) -> None:
    if not isinstance(providers, dict):
        return

    for provider_config in providers.values():
        if isinstance(provider_config, dict):
            provider_config.update(_add_model_alias(provider_config))


def normalize_config(raw_config: dict) -> Dict[str, Any]:
    config = deepcopy(raw_config) if isinstance(raw_config, dict) else {}

    runtime = config.get("runtime")
    if not isinstance(runtime, dict):
        runtime = {}
    else:
        runtime = dict(runtime)

    selected_module = config.get("selected_module")
    if not isinstance(selected_module, dict):
        selected_module = {}

    runtime["llm_profile"] = selected_module.get("llm")
    runtime["asr_profile"] = selected_module.get("asr")
    runtime["tts_profile"] = selected_module.get("tts")
    config["runtime"] = runtime

    for module_name in ("LLM", "ASR", "TTS"):
        _copy_model_name_to_model(config.get(module_name))

    return config


def resolve_llm_config(config: dict) -> Dict[str, Any]:
    selected_module = config.get("selected_module", {})
    runtime = config.get("runtime", {})
    llm_configs = config.get("LLM", {})

    logical_module_name = selected_module.get("LLM")
    base_cfg = llm_configs.get(logical_module_name, {})

    llm_profile = runtime.get("llm_profile")
    if llm_profile and llm_profile in llm_configs:
        final_cfg = dict(base_cfg)
        final_cfg.update(llm_configs[llm_profile])
    else:
        final_cfg = dict(base_cfg)

    return _add_model_alias(final_cfg)


def resolve_asr_config(config: dict) -> Dict[str, Any]:
    selected_module = config.get("selected_module", {})
    runtime = config.get("runtime", {})
    asr_configs = config.get("ASR", {})

    logical_module_name = selected_module.get("ASR")
    base_cfg = asr_configs.get(logical_module_name, {})

    asr_profile = runtime.get("asr_profile")
    if asr_profile and asr_profile in asr_configs:
        final_cfg = dict(base_cfg)
        final_cfg.update(asr_configs[asr_profile])
    else:
        final_cfg = dict(base_cfg)

    return _add_model_alias(final_cfg)


def resolve_tts_config(config: dict) -> Dict[str, Any]:
    selected_module = config.get("selected_module", {})
    runtime = config.get("runtime", {})
    tts_configs = config.get("TTS", {})

    logical_module_name = selected_module.get("TTS")
    base_cfg = tts_configs.get(logical_module_name, {})

    tts_profile = runtime.get("tts_profile")
    if tts_profile and tts_profile in tts_configs:
        final_cfg = dict(base_cfg)
        final_cfg.update(tts_configs[tts_profile])
    else:
        final_cfg = dict(base_cfg)

    return _add_model_alias(final_cfg)
