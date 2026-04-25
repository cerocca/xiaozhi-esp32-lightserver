from fastapi import APIRouter, Query, Request
from fastapi.templating import Jinja2Templates

from app.config import TEMPLATES_DIR
from app.services.device_service import parse_devices_from_logs

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/devices")
def devices_page(
    request: Request,
    lines: int = Query(500),
):
    devices = parse_devices_from_logs(lines)

    return templates.TemplateResponse(
        request,
        "devices.html",
        {
            "request": request,
            "page_title": "Devices",
            "devices": devices,
            "lines": lines,
        },
    )
