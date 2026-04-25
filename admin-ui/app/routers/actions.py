from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.command_service import run_command

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/actions/xserver/restart")
def restart_xserver(request: Request):
    result = run_command(
        [settings.xserver_script_path, "restart"],
        timeout=30,
    )
    return templates.TemplateResponse(
        request,
        "action_result.html",
        {
            "request": request,
            "title": "Restart Xiaozhi server",
            "result": result,
        },
    )


@router.post("/actions/piper/restart")
def restart_piper(request: Request):
    result = run_command(
        [settings.piper_script_path, "restart"],
        timeout=30,
    )
    return templates.TemplateResponse(
        request,
        "action_result.html",
        {
            "request": request,
            "title": "Restart Piper",
            "result": result,
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
