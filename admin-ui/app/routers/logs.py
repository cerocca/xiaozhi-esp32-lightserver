from fastapi import APIRouter, Query, Request
from fastapi.templating import Jinja2Templates

from app.services.log_service import get_piper_logs, get_xserver_logs

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/logs")
def logs_page(
    request: Request,
    source: str = Query("xserver"),
    lines: int = Query(200),
    refresh: int = Query(0),
):
    if source == "piper":
        result = get_piper_logs(lines)
        source_label = "Piper"
    else:
        source = "xserver"
        result = get_xserver_logs(lines)
        source_label = "Xiaozhi server"

    return templates.TemplateResponse(
        request,
        "logs.html",
        {
            "request": request,
            "page_title": "Logs",
            "source": source,
            "source_label": source_label,
            "lines": lines,
            "refresh": refresh,
            "result": result,
        },
    )
