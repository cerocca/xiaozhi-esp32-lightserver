from pathlib import Path

from app.services.config_service import BACKUP_DIR, list_backups as list_backup_entries


def list_backups():
    return list_backup_entries()


def get_backups_state(result=None) -> dict:
    return {
        "backups": list_backups(),
        "result": result,
    }


def delete_backup(filename: str) -> dict:
    try:
        safe_filename = Path(str(filename or "")).name
        if not safe_filename or safe_filename != str(filename):
            return {"ok": False, "message": "Nome backup non valido"}

        path = BACKUP_DIR / safe_filename

        if not path.is_file():
            return {"ok": False, "message": "File non trovato"}

        path.unlink()
        return {"ok": True, "message": f"Backup eliminato: {safe_filename}"}

    except Exception as e:
        return {"ok": False, "message": str(e)}


def delete_all_backups() -> dict:
    try:
        if not BACKUP_DIR.exists():
            return {"ok": True, "message": "Nessun backup presente"}

        count = 0
        for path in BACKUP_DIR.glob("*.config.yaml"):
            if path.is_file():
                path.unlink()
                count += 1

        return {"ok": True, "message": f"{count} backup eliminati"}

    except Exception as e:
        return {"ok": False, "message": str(e)}
