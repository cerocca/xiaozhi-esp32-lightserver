from copy import deepcopy
from typing import Any, Dict


def _copy_model_name_to_model(providers: Any) -> None:
    if not isinstance(providers, dict):
        return

    for provider_config in providers.values():
        if (
            isinstance(provider_config, dict)
            and "model_name" in provider_config
            and "model" not in provider_config
        ):
            provider_config["model"] = provider_config["model_name"]


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
    runtime["asr_profile"] = None
    runtime["tts_profile"] = None
    config["runtime"] = runtime

    for module_name in ("LLM", "ASR", "TTS"):
        _copy_model_name_to_model(config.get(module_name))

    return config
