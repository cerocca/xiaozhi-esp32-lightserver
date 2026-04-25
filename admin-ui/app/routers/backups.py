from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.backup_service import (
    delete_backup,
    delete_all_backups,
    get_backups_state,
)
from app.services.config_service import restore_backup

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/backups")
def backups_page(request: Request):
    return templates.TemplateResponse(
        request,
        "backups.html",
        {
            "request": request,
            "page_title": "Backups",
            **get_backups_state(),
        },
    )


@router.post("/backups/restore")
async def restore_backup_route(request: Request):
    form = await request.form()
    filename = form.get("filename")
    result = restore_backup(filename)

    return templates.TemplateResponse(
        request,
        "backups.html",
        {
            "request": request,
            "page_title": "Backups",
            **get_backups_state(result),
        },
    )


@router.post("/backups/delete")
async def delete_backup_route(request: Request):
    form = await request.form()
    filename = form.get("filename")

    result = delete_backup(filename)

    return templates.TemplateResponse(
        request,
        "backups.html",
        {
            "request": request,
            "page_title": "Backups",
            **get_backups_state(result),
        },
    )


@router.post("/backups/delete-all")
async def delete_all_backups_route(request: Request):
    result = delete_all_backups()

    return templates.TemplateResponse(
        request,
        "backups.html",
        {
            "request": request,
            "page_title": "Backups",
            **get_backups_state(result),
        },
    )
