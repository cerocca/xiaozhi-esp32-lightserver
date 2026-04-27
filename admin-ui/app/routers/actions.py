from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.config import TEMPLATES_DIR, settings
from app.services.command_service import run_command
from app.services.health_service import get_health_status

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.post("/actions/xserver/restart")
def restart_xserver(request: Request):
    result = run_command(
        [settings.xserver_script_path, "restart"],
        timeout=30,
    )
    health_status = get_health_status()
    return templates.TemplateResponse(
        request,
        "action_result.html",
        {
            "request": request,
            "title": "Restart Xiaozhi server",
            "result": result,
            "health_status": health_status,
            "health_snapshot_title": "Post-restart health snapshot",
            "health_snapshot_focus": "Runtime overview after Xiaozhi restart",
            "logs_href": "/logs?source=xserver&lines=200",
            "logs_label": "View Xiaozhi logs",
            "stack_href": "/ai",
            "stack_label": "Open AI Stack",
            "health_note": "Also check /api/health or AI Stack only as operational context, not as proof of the exact active profile.",
        },
    )


@router.post("/actions/piper/restart")
def restart_piper(request: Request):
    result = run_command(
        [settings.piper_script_path, "restart"],
        timeout=30,
    )
    health_status = get_health_status()
    return templates.TemplateResponse(
        request,
        "action_result.html",
        {
            "request": request,
            "title": "Restart Piper",
            "result": result,
            "health_status": health_status,
            "health_snapshot_title": "Post-restart health snapshot",
            "health_snapshot_focus": "Operational TTS focus after Piper restart",
            "logs_href": "/logs?source=piper&lines=200",
            "logs_label": "View Piper logs",
            "stack_href": "/ai",
            "stack_label": "Open AI Stack",
            "health_note": "Also check /api/health or AI Stack only as operational context, not as proof of the exact active profile.",
        },
    )


@router.post("/actions/stop-xiaozhi")
def stop_xiaozhi(request: Request):
    result = run_command(
        ["/bin/bash", "-lc", f"cd {settings.xiaozhi_dir} && docker compose stop"],
        timeout=30,
    )
    return templates.TemplateResponse(
        request,
        "action_result.html",
        {
            "request": request,
            "title": "Stop Xiaozhi server",
            "result": result,
        },
    )


@router.post("/actions/stop-piper")
def stop_piper(request: Request):
    result = run_command(
        ["systemctl", "stop", settings.piper_service_name],
        timeout=30,
    )
    return templates.TemplateResponse(
        request,
        "action_result.html",
        {
            "request": request,
            "title": "Stop Piper",
            "result": result,
        },
    )
