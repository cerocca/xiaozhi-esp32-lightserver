from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates

from app.services.config_service import (
    get_config_editor_state,
    load_config_editor_state,
    save_config,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/config")
def config_page(request: Request):
    editor_state = load_config_editor_state()

    return templates.TemplateResponse(
        request,
        "config_editor.html",
        {
            "request": request,
            "page_title": "Config Editor",
            **editor_state,
        },
    )


@router.post("/config/save")
def config_save(request: Request, content: str = Form(...)):
    editor_state = get_config_editor_state(content)
    result = save_config(content) if editor_state["valid"] else {
        "ok": False,
        "message": editor_state["validation_message"],
    }

    return templates.TemplateResponse(
        request,
        "config_editor.html",
        {
            "request": request,
            "page_title": "Config Editor",
            **get_config_editor_state(content, result=result),
        },
    )
