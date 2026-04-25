from urllib.parse import urlencode

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.command_service import run_command
from app.services.llm_service import (
    create_provider_profile,
    delete_provider_profile,
    get_llm_page_data,
    normalize_llm_form_data,
    set_active_llm,
    update_single_provider,
    update_llm_config,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _render_llm_page(
    request: Request,
    page_data,
    result,
):
    safe_page_data = page_data if isinstance(page_data, dict) else {}
    context = {
        "request": request,
        "page_title": "LLM Config",
        "presets": safe_page_data.get("presets", {}),
        "profiles": safe_page_data.get("profiles", []),
        "selected": safe_page_data.get("selected", {}),
        "active": safe_page_data.get("active", {}),
        "runtime_llm_profile": safe_page_data.get("runtime_llm_profile", ""),
        "legacy_selected_module_name": safe_page_data.get("legacy_selected_module_name", ""),
        "result": result,
    }

    return templates.TemplateResponse(
        request,
        "llm.html",
        context,
    )


def _build_redirect_url(
    profile_name: str = "",
    result: dict | None = None,
) -> str:
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
        selected_module_name = str(result.get("selected_module_name", "") or "").strip()
        if selected_module_name:
            params["selected_module_name"] = selected_module_name
        active_model = str(result.get("active_model", "") or "").strip()
        if active_model:
            params["active_model"] = active_model

    if not params:
        return "/llm"

    return f"/llm?{urlencode(params)}"


def _get_result_from_query(ok: str, msg: str, backup_path: str, selected_module_name: str, active_model: str):
    has_flash = any([ok, msg, backup_path, selected_module_name, active_model])
    if not has_flash:
        return None

    flash_ok = str(ok or "").strip() == "1"
    return {
        "ok": flash_ok,
        "message": str(msg or "").strip(),
        "backup_path": str(backup_path or "").strip(),
        "selected_module_name": str(selected_module_name or "").strip(),
        "active_model": str(active_model or "").strip(),
    }


def _save_llm(
    profile_name: str,
    provider_id: str,
    api_key: str,
    model: str,
    base_url: str,
    temperature: float,
    restart=False,
):
    form_data = normalize_llm_form_data(
        provider_id,
        api_key,
        model,
        base_url,
        temperature,
    )

    result = update_single_provider(
        profile_name=profile_name,
        provider_id=form_data["provider"],
        patch={
            "api_key": form_data["api_key"],
            "model": form_data["model"],
            "base_url": form_data["base_url"],
            "temperature": form_data["temperature"],
        },
    )

    if restart and result.get("ok"):
        restart_result = run_command(
            [settings.xserver_script_path, "restart"],
            timeout=30,
        )
        result["restart_result"] = restart_result
        if restart_result.get("ok"):
            result["message"] = f'{result["message"]} + restart Xiaozhi completato'
        else:
            result["message"] = f'{result["message"]} ma restart Xiaozhi fallito'

    selected_profile_name = profile_name
    if result.get("ok") and result.get("selected_module_name"):
        selected_profile_name = result["selected_module_name"]
    return result, selected_profile_name


@router.get("/llm")
def llm_page(
    request: Request,
    profile: str = Query(default=""),
    ok: str = Query(default=""),
    msg: str = Query(default=""),
    backup_path: str = Query(default=""),
    selected_module_name: str = Query(default=""),
    active_model: str = Query(default=""),
):
    page_data = get_llm_page_data(selected_profile_name=profile)
    result = _get_result_from_query(ok, msg, backup_path, selected_module_name, active_model)
    return _render_llm_page(request, page_data, result)


@router.post("/llm/providers/save")
def llm_save_provider(
    request: Request,
    profile_name: str = Form(...),
    provider_id: str = Form(...),
    api_key: str = Form(...),
    model: str = Form(...),
    base_url: str = Form(...),
    temperature: float = Form(...),
):
    result, selected_profile_name = _save_llm(
        profile_name,
        provider_id,
        api_key,
        model,
        base_url,
        temperature,
    )
    redirect_url = _build_redirect_url(profile_name=selected_profile_name, result=result)
    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/llm/save")
def llm_save_legacy(
    request: Request,
    provider: str = Form(...),
    api_key: str = Form(...),
    model: str = Form(...),
    base_url: str = Form(...),
    temperature: float = Form(...),
):
    result = update_llm_config(
        provider=provider,
        api_key=api_key,
        model=model,
        base_url=base_url,
        temperature=temperature,
    )
    selected_profile_name = result.get("selected_module_name", provider)
    redirect_url = _build_redirect_url(profile_name=selected_profile_name, result=result)
    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/llm/save-and-restart")
def llm_save_and_restart_legacy(
    request: Request,
    provider: str = Form(...),
    api_key: str = Form(...),
    model: str = Form(...),
    base_url: str = Form(...),
    temperature: float = Form(...),
):
    result = update_llm_config(
        provider=provider,
        api_key=api_key,
        model=model,
        base_url=base_url,
        temperature=temperature,
    )

    if result.get("ok"):
        restart_result = run_command(
            [settings.xserver_script_path, "restart"],
            timeout=30,
        )
        result["restart_result"] = restart_result
        if restart_result.get("ok"):
            result["message"] = f'{result["message"]} + restart Xiaozhi completato'
        else:
            result["message"] = f'{result["message"]} ma restart Xiaozhi fallito'

    selected_profile_name = result.get("selected_module_name", provider)
    redirect_url = _build_redirect_url(profile_name=selected_profile_name, result=result)
    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/llm/providers/switch")
def llm_switch_provider(
    request: Request,
    profile_name: str = Form(...),
):
    result = set_active_llm(profile_name)
    selected_profile_name = result.get("selected_module_name", profile_name)
    redirect_url = _build_redirect_url(profile_name=selected_profile_name, result=result)
    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/llm/providers/create")
def llm_create_provider(
    request: Request,
    provider_id: str = Form(...),
    profile_name: str = Form(default=""),
):
    result = create_provider_profile(provider_id=provider_id, profile_name=profile_name or None)
    selected_profile_name = result.get("selected_module_name", profile_name)
    redirect_url = _build_redirect_url(profile_name=selected_profile_name, result=result)
    return RedirectResponse(url=redirect_url, status_code=303)


@router.post("/llm/providers/delete")
def llm_delete_provider(
    request: Request,
    profile_name: str = Form(...),
    selected_profile_name: str = Form(default=""),
):
    result = delete_provider_profile(profile_name=profile_name)

    next_selected_profile_name = selected_profile_name
    if result.get("ok") and selected_profile_name == profile_name:
        next_selected_profile_name = ""

    if result.get("ok"):
        next_selected_profile_name = result.get("selected_module_name", next_selected_profile_name)
    redirect_url = _build_redirect_url(profile_name=next_selected_profile_name, result=result)
    return RedirectResponse(url=redirect_url, status_code=303)
