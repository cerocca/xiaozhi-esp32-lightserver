from app.config import settings
from app.services.command_service import run_command


def get_xserver_logs(lines: int = 200) -> dict:
    return run_command(
        [
            settings.xserver_script_path,
            "logs-web",
            str(lines),
        ],
        timeout=20,
    )


def get_piper_logs(lines: int = 200) -> dict:
    return run_command(
        [
            settings.piper_script_path,
            "logs-web",
            str(lines),
        ],
        timeout=20,
    )
