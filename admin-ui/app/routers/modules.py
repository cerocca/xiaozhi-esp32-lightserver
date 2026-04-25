from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.module_readonly_service import get_module_readonly_page_data

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _render_module_page(request: Request, slug: str):
    page_data = get_module_readonly_page_data(slug)
    return templates.TemplateResponse(
        request,
        "module_readonly.html",
        {
            "request": request,
            **page_data,
        },
    )


@router.get("/vad")
def vad_page(request: Request):
    return _render_module_page(request, "vad")


@router.get("/intent")
def intent_page(request: Request):
    return _render_module_page(request, "intent")


@router.get("/memory")
def memory_page(request: Request):
    return _render_module_page(request, "memory")
