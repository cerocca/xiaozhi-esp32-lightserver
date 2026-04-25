from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR = BASE_DIR / "app" / "static"


def _detect_backend_root() -> Path:
    monorepo_root = BASE_DIR.parent
    legacy_sibling_root = BASE_DIR.parent / "xiaozhi-esp32-lightserver"

    for candidate in (monorepo_root, legacy_sibling_root):
        if (candidate / "docker-compose.yml").exists():
            return candidate

    return legacy_sibling_root


def _resolve_repo_path(value: str) -> str:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()
    return str(path)


DEFAULT_BACKEND_ROOT = _detect_backend_root()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8")

    admin_ui_version: str = "0.1.5"
    admin_ui_repo_url: str = "https://github.com/cerocca/xiaozhi-admin-ui"

    admin_ui_host: str = "192.168.1.69"
    admin_ui_port: int = 8088
    backend_host: str = "127.0.0.1"
    backend_health_port: int = 8003

    xiaozhi_dir: str = str(DEFAULT_BACKEND_ROOT)
    xiaozhi_config: str = str(DEFAULT_BACKEND_ROOT / "data" / ".config.yaml")
    xserver_service_name: str = "xiaozhi-server"
    piper_service_name: str = "piper-api"
    xserver_script_path: str = "scripts/xserver.sh"
    piper_script_path: str = "scripts/piper.sh"

    piper_health_url: str = "http://127.0.0.1:8091/health"

    lan_cidr: str = "192.168.1.0/24"

    def model_post_init(self, __context) -> None:
        self.xiaozhi_dir = _resolve_repo_path(self.xiaozhi_dir)
        self.xiaozhi_config = _resolve_repo_path(self.xiaozhi_config)
        self.xserver_script_path = _resolve_repo_path(self.xserver_script_path)
        self.piper_script_path = _resolve_repo_path(self.piper_script_path)


settings = Settings()
