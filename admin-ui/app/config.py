from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    admin_ui_version: str = "0.1.5"
    admin_ui_repo_url: str = "https://github.com/cerocca/xiaozhi-admin-ui"

    admin_ui_host: str = "192.168.1.69"
    admin_ui_port: int = 8088
    backend_host: str = "127.0.0.1"
    backend_health_port: int = 8003

    xiaozhi_dir: str = "/home/ciru/xiaozhi-esp32-lightserver"
    xiaozhi_config: str = "/home/ciru/xiaozhi-esp32-lightserver/data/.config.yaml"
    xserver_service_name: str = "xiaozhi-server"
    piper_service_name: str = "piper-api"
    xserver_script_path: str = str(BASE_DIR / "scripts" / "xserver.sh")
    piper_script_path: str = str(BASE_DIR / "scripts" / "piper.sh")

    piper_health_url: str = "http://127.0.0.1:8091/health"

    lan_cidr: str = "192.168.1.0/24"


settings = Settings()
