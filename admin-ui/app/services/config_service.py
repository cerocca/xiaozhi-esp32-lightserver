from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import yaml

from app.config import BASE_DIR, settings


BACKUP_DIR = BASE_DIR / "data" / "backups" / "config"


def get_config_path() -> Path:
    return Path(settings.xiaozhi_config)


def ensure_backup_dir() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    return BACKUP_DIR


def read_config_text() -> str:
    path = get_config_path()
    return path.read_text(encoding="utf-8")


def validate_yaml_text(content: str) -> tuple[bool, str]:
    try:
        data = yaml.safe_load(content)
        if data is None:
            return False, "Il file YAML non può essere vuoto"
        if not isinstance(data, dict):
            return False, "La root del config deve essere una mappa YAML"
        return True, "YAML valido"
    except yaml.YAMLError as e:
        return False, str(e)


def get_config_editor_state(content: str, result=None) -> dict:
    valid, validation_message = validate_yaml_text(content)
    return {
        "content": content,
        "valid": valid,
        "validation_message": validation_message,
        "result": result,
    }


def load_config_editor_state(result=None) -> dict:
    try:
        content = read_config_text()
    except OSError as e:
        return {
            "content": "",
            "valid": False,
            "validation_message": f"Impossibile leggere la config corrente: {e}",
            "result": result,
        }

    return get_config_editor_state(content, result=result)


def compute_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def create_backup() -> Path:
    src = get_config_path()
    if not src.exists():
        raise FileNotFoundError(f"Config non trovata: {src}")

    ensure_backup_dir()
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")
    dst = BACKUP_DIR / f"{timestamp}.config.yaml"
    shutil.copy2(src, dst)
    return dst


def atomic_write_config(content: str) -> None:
    target = get_config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(target.parent),
            delete=False,
        ) as tmp:
            tmp.write(content)
            tmp.flush()
            os.fsync(tmp.fileno())
            temp_name = tmp.name

        os.replace(temp_name, target)
    except OSError:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)
        raise


def _verify_saved_config(content: str) -> tuple[bool, str]:
    try:
        saved_content = read_config_text()
    except OSError as e:
        return False, f"Verifica post-write fallita: {e}"

    valid, message = validate_yaml_text(saved_content)
    if not valid:
        return False, f"Verifica post-write fallita: {message}"

    if compute_sha256(saved_content) != compute_sha256(content):
        return False, "Verifica post-write fallita: contenuto finale diverso da quello richiesto"

    return True, "ok"


def save_config(content: str) -> dict:
    valid, message = validate_yaml_text(content)
    if not valid:
        return {
            "ok": False,
            "message": f"Validazione YAML fallita: {message}",
        }

    try:
        backup_path = create_backup()
    except FileNotFoundError as e:
        return {"ok": False, "message": str(e)}
    except OSError as e:
        return {"ok": False, "message": f"Backup config fallito: {e}"}

    try:
        atomic_write_config(content)
    except OSError as e:
        return {
            "ok": False,
            "message": f"Scrittura config fallita: {e}",
            "backup_path": str(backup_path),
        }

    verified, verify_message = _verify_saved_config(content)
    if not verified:
        return {
            "ok": False,
            "message": verify_message,
            "backup_path": str(backup_path),
        }

    return {
        "ok": True,
        "message": "Config salvata correttamente",
        "backup_path": str(backup_path),
        "sha256": compute_sha256(content),
    }


def list_backups() -> list[dict]:
    ensure_backup_dir()
    backups = []

    for path in sorted(BACKUP_DIR.glob("*.config.yaml"), reverse=True):
        try:
            text = path.read_text(encoding="utf-8")
            stat = path.stat()
        except OSError:
            continue
        except UnicodeDecodeError:
            continue
        backups.append(
            {
                "name": path.name,
                "path": str(path),
                "size": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "sha256_short": compute_sha256(text)[:12],
            }
        )

    return backups


def restore_backup(filename: str) -> dict:
    ensure_backup_dir()
    safe_filename = Path(str(filename or "")).name
    if not safe_filename or safe_filename != str(filename):
        return {"ok": False, "message": "Nome backup non valido"}

    backup_file = BACKUP_DIR / safe_filename

    if not backup_file.exists():
        return {"ok": False, "message": f"Backup non trovato: {safe_filename}"}

    content = backup_file.read_text(encoding="utf-8")
    valid, message = validate_yaml_text(content)
    if not valid:
        return {
            "ok": False,
            "message": f"Il backup non contiene YAML valido: {message}",
        }

    try:
        current_backup = create_backup()
    except FileNotFoundError as e:
        return {"ok": False, "message": str(e)}
    except OSError as e:
        return {"ok": False, "message": f"Backup pre-restore fallito: {e}"}

    try:
        atomic_write_config(content)
    except OSError as e:
        return {
            "ok": False,
            "message": f"Restore backup fallito: {e}",
            "pre_restore_backup": str(current_backup),
        }

    verified, verify_message = _verify_saved_config(content)
    if not verified:
        return {
            "ok": False,
            "message": verify_message,
            "pre_restore_backup": str(current_backup),
        }

    return {
        "ok": True,
        "message": "Rollback completato",
        "restored_from": safe_filename,
        "pre_restore_backup": str(current_backup),
    }
