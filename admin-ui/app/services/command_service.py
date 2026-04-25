import subprocess


def run_command(cmd: list[str], timeout: int = 20) -> dict:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as e:
        return {
            "ok": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
        }
