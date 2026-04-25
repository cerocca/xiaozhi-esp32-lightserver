import yaml

from app.services.config_service import read_config_text


MODULE_META = {
    "vad": {
        "section": "VAD",
        "selected_key": "VAD",
        "legacy_selected_key": "vad",
        "title": "VAD",
        "page_title": "VAD",
        "description": "Voice Activity Detection: decide quando l'audio contiene davvero voce e quando la pipeline deve iniziare o fermarsi.",
    },
    "intent": {
        "section": "Intent",
        "selected_key": "Intent",
        "legacy_selected_key": "intent",
        "title": "Intent",
        "page_title": "Intent",
        "description": "Intent: interpreta la richiesta e decide eventuali azioni o instradamenti semantici prima della risposta finale.",
    },
    "memory": {
        "section": "Memory",
        "selected_key": "Memory",
        "legacy_selected_key": "memory",
        "title": "Memory",
        "page_title": "Memory",
        "description": "Memory: controlla se e come il backend conserva contesto o ricordi locali oltre il singolo turno.",
    },
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


def _get_dict(data: dict, key: str) -> dict:
    value = data.get(key, {})
    if isinstance(value, dict):
        return value
    return {}


def get_module_readonly_page_data(slug: str) -> dict:
    meta = MODULE_META.get(slug)
    if not meta:
        return {}

    data = _safe_load_config_data()
    selected_module = _get_dict(data, "selected_module")
    section_name = meta["section"]
    section_map = _get_dict(data, section_name)
    current_module_name = str(selected_module.get(meta["selected_key"], "") or "").strip()
    if not current_module_name:
        current_module_name = str(selected_module.get(meta["legacy_selected_key"], "") or "").strip()

    if not isinstance(section_map.get(current_module_name), dict):
        for candidate_name, candidate_block in section_map.items():
            if isinstance(candidate_block, dict):
                current_module_name = str(candidate_name)
                break

    current_block = section_map.get(current_module_name, {})
    if not isinstance(current_block, dict):
        current_block = {}

    relevant_keys = []
    for key, value in current_block.items():
        if isinstance(value, (dict, list)):
            rendered_value = yaml.safe_dump(value, allow_unicode=True, sort_keys=False).strip()
        else:
            rendered_value = str(value)
        relevant_keys.append({"key": key, "value": rendered_value})

    return {
        "slug": slug,
        "page_title": meta["page_title"],
        "module_title": meta["title"],
        "description": meta["description"],
        "section_name": section_name,
        "current_module_name": current_module_name,
        "selected_key": meta["selected_key"],
        "current_block": current_block,
        "current_block_yaml": yaml.safe_dump(current_block, allow_unicode=True, sort_keys=False).strip()
        if current_block
        else "",
        "relevant_keys": relevant_keys,
    }
