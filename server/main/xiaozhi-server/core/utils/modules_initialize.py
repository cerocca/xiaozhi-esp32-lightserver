from typing import Dict, Any
from config.logger import setup_logging
from core.utils import tts, llm, intent, memory, vad, asr
from core.utils.config_normalizer import (
    normalize_config,
    resolve_asr_config,
    resolve_llm_config,
    resolve_tts_config,
)

TAG = __name__
logger = setup_logging()


def initialize_modules(
    logger,
    config: Dict[str, Any],
    init_vad=False,
    init_asr=False,
    init_llm=False,
    init_tts=False,
    init_memory=False,
    init_intent=False,
) -> Dict[str, Any]:
    """
    初始化所有模块组件

    Args:
        config: 配置字典

    Returns:
        Dict[str, Any]: 包含所有初始化后的模块的字典
    """
    config = normalize_config(config)
    llm_cfg = resolve_llm_config(config)
    asr_cfg = resolve_asr_config(config)
    tts_cfg = resolve_tts_config(config)
    logger.bind(tag=TAG).info(
        "配置归一化完成，"
        f"runtime.llm_profile={config['runtime']['llm_profile']}, "
        f"runtime.asr_profile={config['runtime']['asr_profile']}, "
        f"runtime.tts_profile={config['runtime']['tts_profile']}"
    )

    modules = {}

    # 初始化TTS模块
    if init_tts:
        select_tts_module = config["selected_module"]["TTS"]
        modules["tts"] = initialize_tts(config, tts_cfg)
        logger.bind(tag=TAG).info(f"初始化组件: tts成功 {select_tts_module}")

    # 初始化LLM模块
    if init_llm:
        select_llm_module = config["selected_module"]["LLM"]
        llm_type = (
            select_llm_module
            if "type" not in llm_cfg
            else llm_cfg["type"]
        )
        modules["llm"] = llm.create_instance(
            llm_type,
            llm_cfg,
        )
        logger.bind(tag=TAG).info(f"初始化组件: llm成功 {select_llm_module}")

    # 初始化Intent模块
    if init_intent:
        select_intent_module = config["selected_module"]["Intent"]
        intent_type = (
            select_intent_module
            if "type" not in config["Intent"][select_intent_module]
            else config["Intent"][select_intent_module]["type"]
        )
        modules["intent"] = intent.create_instance(
            intent_type,
            config["Intent"][select_intent_module],
        )
        logger.bind(tag=TAG).info(f"初始化组件: intent成功 {select_intent_module}")

    # 初始化Memory模块
    if init_memory:
        select_memory_module = config["selected_module"]["Memory"]
        memory_type = (
            select_memory_module
            if "type" not in config["Memory"][select_memory_module]
            else config["Memory"][select_memory_module]["type"]
        )
        modules["memory"] = memory.create_instance(
            memory_type,
            config["Memory"][select_memory_module],
            config.get("summaryMemory", None),
        )
        logger.bind(tag=TAG).info(f"初始化组件: memory成功 {select_memory_module}")

    # 初始化VAD模块
    if init_vad:
        select_vad_module = config["selected_module"]["VAD"]
        vad_type = (
            select_vad_module
            if "type" not in config["VAD"][select_vad_module]
            else config["VAD"][select_vad_module]["type"]
        )
        modules["vad"] = vad.create_instance(
            vad_type,
            config["VAD"][select_vad_module],
        )
        logger.bind(tag=TAG).info(f"初始化组件: vad成功 {select_vad_module}")

    # 初始化ASR模块
    if init_asr:
        select_asr_module = config["selected_module"]["ASR"]
        modules["asr"] = initialize_asr(config, asr_cfg)
        logger.bind(tag=TAG).info(f"初始化组件: asr成功 {select_asr_module}")
    return modules


def initialize_tts(config, tts_cfg=None):
    select_tts_module = config["selected_module"]["TTS"]
    if tts_cfg is None:
        tts_cfg = resolve_tts_config(config)
    tts_type = (
        select_tts_module
        if "type" not in tts_cfg
        else tts_cfg["type"]
    )
    new_tts = tts.create_instance(
        tts_type,
        tts_cfg,
        str(config.get("delete_audio", True)).lower() in ("true", "1", "yes"),
    )
    return new_tts


def initialize_asr(config, asr_cfg=None):
    select_asr_module = config["selected_module"]["ASR"]
    if asr_cfg is None:
        asr_cfg = resolve_asr_config(config)
    asr_type = (
        select_asr_module
        if "type" not in asr_cfg
        else asr_cfg["type"]
    )
    new_asr = asr.create_instance(
        asr_type,
        asr_cfg,
        str(config.get("delete_audio", True)).lower() in ("true", "1", "yes"),
    )
    logger.bind(tag=TAG).info("ASR模块初始化完成")
    return new_asr


def initialize_voiceprint(asr_instance, config):
    """初始化声纹识别功能"""
    voiceprint_config = config.get("voiceprint")
    if not voiceprint_config:
        return False  

    # 应用配置
    if not voiceprint_config.get("url") or not voiceprint_config.get("speakers"):
        logger.bind(tag=TAG).warning("声纹识别配置不完整")
        return False
        
    try:
        asr_instance.init_voiceprint(voiceprint_config)
        logger.bind(tag=TAG).info("ASR模块声纹识别功能已动态启用")
        logger.bind(tag=TAG).info(f"配置说话人数量: {len(voiceprint_config['speakers'])}")
        return True
    except Exception as e:
        logger.bind(tag=TAG).error(f"动态初始化声纹识别功能失败: {str(e)}")
        return False
