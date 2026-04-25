from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers.actions import router as actions_router
from app.routers.asr import router as asr_router
from app.routers.backups import router as backups_router
from app.routers.config_editor import router as config_router
from app.routers.dashboard import router as dashboard_router
from app.routers.devices import router as devices_router
from app.routers.llm import router as llm_router
from app.routers.logs import router as logs_router
from app.routers.modules import router as modules_router
from app.routers.tts import router as tts_router

app = FastAPI(title="Xiaozhi Admin UI", version=settings.admin_ui_version)
app.state.repo_url = settings.admin_ui_repo_url

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(dashboard_router)
app.include_router(config_router)
app.include_router(actions_router)
app.include_router(logs_router)
app.include_router(devices_router)
app.include_router(llm_router)
app.include_router(asr_router)
app.include_router(tts_router)
app.include_router(modules_router)
app.include_router(backups_router)
