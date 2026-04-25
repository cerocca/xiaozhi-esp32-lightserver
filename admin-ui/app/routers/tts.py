from urllib.parse import urlencode

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.tts_service import (
    create_tts_profile,
    delete_tts_profile,
    get_tts_page_data,
    set_active_tts,
    update_single_tts_profile,
)


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


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

    if not params:
        return "/tts"
    return f"/tts?{urlencode(params)}"


def _get_result_from_query(ok, msg, backup_path):
    if not any([ok, msg, backup_path]):
        return None

    return {
        "ok": str(ok or "").strip() == "1",
        "message": str(msg or "").strip(),
        "backup_path": str(backup_path or "").strip(),
    }


@router.get("/tts")
def tts_page(
    request: Request,
    profile: str = Query(default=""),
    ok: str = Query(default=""),
    msg: str = Query(default=""),
    backup_path: str = Query(default=""),
):
    page_data = get_tts_page_data(selected_profile_name=profile)
    result = _get_result_from_query(ok, msg, backup_path)
    return _render_tts_page(request, page_data, result)


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
