from urllib.parse import urlencode

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import TEMPLATES_DIR
from app.services.health_service import get_health_status
from app.services.tts_service import (
    create_tts_profile,
    delete_tts_profile,
    get_tts_page_data,
    set_active_tts,
    test_active_tts,
    update_single_tts_profile,
)


router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _render_tts_page(request, page_data, result):
    safe_page_data = page_data if isinstance(page_data, dict) else {}
    context = {
        "request": request,
        "page_title": "TTS",
        "presets": safe_page_data.get("presets", {}),
        "profiles": safe_page_data.get("profiles", []),
        "selected": safe_page_data.get("selected", {}),
        "active": safe_page_data.get("active", {}),
        "runtime_tts_profile": safe_page_data.get("runtime_tts_profile", ""),
        "legacy_selected_module_name": safe_page_data.get("legacy_selected_module_name", ""),
        "logical_selected_module_name": safe_page_data.get("logical_selected_module_name", ""),
        "health_status": get_health_status(),
        "result": result,
    }
    return templates.TemplateResponse(request, "tts.html", context)


def _build_redirect_url(profile_name="", result=None):
    params = {}
    profile_name = str(profile_name or "").strip()
    if profile_name:
        params["profile"] = profile_name

    if isinstance(result, dict):
        params["ok"] = "1" if bool(result.get("ok")) else "0"
        message = str(result.get("message", "") or "").strip()
        if message:
            params["msg"] = message
        backup_path = str(result.get("backup_path", "") or "").strip()
        if backup_path:
            params["backup_path"] = backup_path
        action_kind = str(result.get("action_kind", "") or "").strip()
        if action_kind:
            params["action_kind"] = action_kind
        selected_profile_name = str(result.get("selected_profile_name", "") or "").strip()
        if selected_profile_name:
            params["selected_profile_name"] = selected_profile_name
        runtime_key = str(result.get("runtime_key", "") or "").strip()
        if runtime_key:
            params["runtime_key"] = runtime_key
        logs_href = str(result.get("logs_href", "") or "").strip()
        if logs_href:
            params["logs_href"] = logs_href
        logs_label = str(result.get("logs_label", "") or "").strip()
        if logs_label:
            params["logs_label"] = logs_label
        validation_status = str(result.get("validation_status", "") or "").strip()
        if validation_status:
            params["validation_status"] = validation_status
        validation_warning_count = str(result.get("validation_warning_count", "") or "").strip()
        if validation_warning_count:
            params["validation_warning_count"] = validation_warning_count
        validation_warnings = result.get("validation_warnings", [])
        if isinstance(validation_warnings, list) and validation_warnings:
            params["validation_warnings"] = "||".join(
                str(item or "").strip() for item in validation_warnings if str(item or "").strip()
            )
        endpoint = str(result.get("endpoint", "") or "").strip()
        if endpoint:
            params["endpoint"] = endpoint
        http_status = str(result.get("http_status", "") or "").strip()
        if http_status:
            params["http_status"] = http_status
        error_reason = str(result.get("error_reason", "") or "").strip()
        if error_reason:
            params["error_reason"] = error_reason
        content_type = str(result.get("content_type", "") or "").strip()
        if content_type:
            params["content_type"] = content_type

    if not params:
        return "/tts"
    return f"/tts?{urlencode(params)}"


def _get_result_from_query(ok, msg, backup_path, action_kind, selected_profile_name, runtime_key, logs_href, logs_label, validation_status, validation_warning_count, validation_warnings, endpoint, http_status, error_reason, content_type):
    if not any([ok, msg, backup_path, action_kind, selected_profile_name, runtime_key, logs_href, logs_label, validation_status, validation_warning_count, validation_warnings, endpoint, http_status, error_reason, content_type]):
        return None

    return {
        "ok": str(ok or "").strip() == "1",
        "message": str(msg or "").strip(),
        "backup_path": str(backup_path or "").strip(),
        "action_kind": str(action_kind or "").strip(),
        "selected_profile_name": str(selected_profile_name or "").strip(),
        "runtime_key": str(runtime_key or "").strip(),
        "logs_href": str(logs_href or "").strip(),
        "logs_label": str(logs_label or "").strip(),
        "validation_status": str(validation_status or "").strip(),
        "validation_warning_count": int(str(validation_warning_count or "0").strip() or "0"),
        "validation_warnings": [item for item in str(validation_warnings or "").split("||") if item.strip()],
        "endpoint": str(endpoint or "").strip(),
        "http_status": str(http_status or "").strip(),
        "error_reason": str(error_reason or "").strip(),
        "content_type": str(content_type or "").strip(),
    }


def _annotate_switch_result(result, profile_name):
    result["action_kind"] = "switch"
    result["selected_profile_name"] = result.get("selected_profile_name", profile_name)
    result["runtime_key"] = "runtime.tts_profile"
    result["logs_href"] = "/logs?source=piper&lines=200"
    result["logs_label"] = "Vedi log Piper"
    return result


@router.get("/tts")
def tts_page(
    request: Request,
    profile: str = Query(default=""),
    ok: str = Query(default=""),
    msg: str = Query(default=""),
    backup_path: str = Query(default=""),
    action_kind: str = Query(default=""),
    selected_profile_name: str = Query(default=""),
    runtime_key: str = Query(default=""),
    logs_href: str = Query(default=""),
    logs_label: str = Query(default=""),
    validation_status: str = Query(default=""),
    validation_warning_count: str = Query(default=""),
    validation_warnings: str = Query(default=""),
    endpoint: str = Query(default=""),
    http_status: str = Query(default=""),
    error_reason: str = Query(default=""),
    content_type: str = Query(default=""),
):
    page_data = get_tts_page_data(selected_profile_name=profile)
    result = _get_result_from_query(
        ok,
        msg,
        backup_path,
        action_kind,
        selected_profile_name,
        runtime_key,
        logs_href,
        logs_label,
        validation_status,
        validation_warning_count,
        validation_warnings,
        endpoint,
        http_status,
        error_reason,
        content_type,
    )
    return _render_tts_page(request, page_data, result)


@router.post("/tts/test")
def tts_test(request: Request):
    result = test_active_tts()
    redirect_url = _build_redirect_url(result.get("selected_profile_name", ""), result)
    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/tts/profiles/save")
def tts_save_profile(
    request: Request,
    profile_name: str = Form(...),
    type: str = Form(...),
    endpoint: str = Form(...),
    model: str = Form(...),
    voice: str = Form(...),
    speed: str = Form(default=""),
    api_key: str = Form(default=""),
    output_dir: str = Form(default=""),
):
    result = update_single_tts_profile(
        profile_name=profile_name,
        patch={
            "type": type,
            "endpoint": endpoint,
            "model": model,
            "voice": voice,
            "speed": speed,
            "api_key": api_key,
            "output_dir": output_dir,
        },
    )
    redirect_url = _build_redirect_url(result.get("selected_profile_name", profile_name), result)
    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/tts/profiles/switch")
def tts_switch_profile(
    request: Request,
    profile_name: str = Form(...),
):
    result = set_active_tts(profile_name)
    result = _annotate_switch_result(result, profile_name)
    redirect_url = _build_redirect_url(result.get("selected_profile_name", profile_name), result)
    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/tts/profiles/create")
def tts_create_profile(
    request: Request,
    provider_id: str = Form(...),
    profile_name: str = Form(default=""),
):
    result = create_tts_profile(provider_id=provider_id, profile_name=profile_name or None)
    redirect_url = _build_redirect_url(result.get("selected_profile_name", profile_name), result)
    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/tts/profiles/delete")
def tts_delete_profile(
    request: Request,
    profile_name: str = Form(...),
    selected_profile_name: str = Form(default=""),
):
    result = delete_tts_profile(profile_name)

    next_selected_profile_name = selected_profile_name
    if result.get("ok") and selected_profile_name == profile_name:
        next_selected_profile_name = result.get("selected_profile_name", "")
    elif not next_selected_profile_name:
        next_selected_profile_name = result.get("selected_profile_name", "")

    redirect_url = _build_redirect_url(next_selected_profile_name, result)
    return RedirectResponse(url=redirect_url, status_code=303)
