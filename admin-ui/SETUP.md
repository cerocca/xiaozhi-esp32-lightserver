# SETUP

This guide covers the simplest path to install `xiaozhi-admin-ui` on a Linux server, with explicit configuration and minimal manual steps.

---

## 1. Prerequisites

You must already have:

- Linux with shell access
- `git`
- Python 3 with `venv`
- a working Xiaozhi backend
- access to the backend config file
- Docker and Docker Compose (for backend)
- Piper (optional)

Compatible backends (examples):
- `xiaozhi-esp32-lightserver`
- `xiaozhi-esp32-server`

Critical requirement:
- `/api/health` endpoint must be available and working

---

## 2. Backend preflight (mandatory)

Verify the backend is actually working:

```bash
ls -ld /home/xiaozhi/xiaozhi-esp32-lightserver
ls -l /home/xiaozhi/xiaozhi-esp32-lightserver/data/.config.yaml

cd /home/xiaozhi/xiaozhi-esp32-lightserver
docker compose ps

curl -s http://127.0.0.1:8003/api/health
```

This must return valid JSON.

If using Piper:

```bash
systemctl status piper-api --no-pager
curl -s http://127.0.0.1:8091/health
```

---

## 3. Installation

```bash
git clone https://github.com/cerocca/xiaozhi-admin-ui.git
cd xiaozhi-admin-ui

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 4. Configuration (.env)

Copy example file:

```bash
cp .env.example .env
```

Edit at least:

```env
ADMIN_UI_HOST=0.0.0.0
ADMIN_UI_PORT=8088

BACKEND_HOST=127.0.0.1
BACKEND_HEALTH_PORT=8003

XIAOZHI_DIR=/home/xiaozhi/xiaozhi-esp32-lightserver
XIAOZHI_CONFIG=/home/xiaozhi/xiaozhi-esp32-lightserver/data/.config.yaml

PIPER_SERVICE_NAME=piper-api
```

---

## 5. What to verify (important)

Always verify:

- `XIAOZHI_DIR`
- `XIAOZHI_CONFIG`

They must match real backend paths on the machine.

Adjust if needed:

- `ADMIN_UI_HOST`
- `ADMIN_UI_PORT`
- `BACKEND_HOST`
- `BACKEND_HEALTH_PORT`
- `PIPER_SERVICE_NAME`

Optional (defaults are usually correct):

- `XSERVER_SCRIPT_PATH`
- `PIPER_SCRIPT_PATH`
- `XSERVER_SERVICE_NAME`
- `PIPER_HEALTH_URL`
- `LAN_CIDR`

Defaults:

- scripts paths point to repo-local scripts
- Piper health defaults to `http://127.0.0.1:8091/health`
- LAN_CIDR defaults to `192.168.1.0/24`
- XSERVER_SERVICE_NAME defaults to `xiaozhi-server`

Notes:

- `ADMIN_UI_HOST=0.0.0.0` is the easiest option for LAN access
- backend host/port must expose `/api/health`
- config file must be writable by the UI user

---

## 6. Run manually

```bash
cd /home/xiaozhi/xiaozhi-admin-ui
source .venv/bin/activate

python -c "import app.main; print('import ok')"
uvicorn app.main:app --host 0.0.0.0 --port 8088
```

Open:

```
http://<SERVER_IP>:8088
```

---

## 7. Verification

```bash
curl -I http://<SERVER_IP>:8088
curl -s http://127.0.0.1:8003/api/health
```

UI checks:

- `/` loads correctly
- dashboard shows runtime status
- `/config` reads real YAML
- `/logs` shows backend and Piper output
- `/devices` loads

Notes:

- `device = disconnected` is normal if no device is connected
- if `/api/health` is unreachable, UI shows `UNKNOWN` (not an error)
- Piper is optional and does not block the UI

---

## 8. systemd (recommended)

File:

```
/etc/systemd/system/xiaozhi-admin-ui.service
```

Content:

```ini
[Unit]
Description=Xiaozhi Admin UI
After=network-online.target

[Service]
Type=simple
User=xiaozhi
WorkingDirectory=/home/xiaozhi/xiaozhi-admin-ui
EnvironmentFile=/home/xiaozhi/xiaozhi-admin-ui/.env
ExecStart=/home/xiaozhi/xiaozhi-admin-ui/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8088
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now xiaozhi-admin-ui
sudo systemctl status xiaozhi-admin-ui --no-pager -l
journalctl -u xiaozhi-admin-ui -f
```

---

## 9. Ports

Typical ports:

- Admin UI: 8088
- backend health: 8003
- Piper health: 8091

```bash
ss -ltnp | grep 8088
curl -I http://<SERVER_IP>:8088
curl -s http://127.0.0.1:8003/api/health
curl -s http://127.0.0.1:8091/health
```

---

## 10. Optional CLI helpers

```bash
nano ~/.bashrc
```

Add:

```bash
alias ui-start="sudo systemctl start xiaozhi-admin-ui"
alias ui-stop="sudo systemctl stop xiaozhi-admin-ui"
alias ui-restart="sudo systemctl restart xiaozhi-admin-ui"
alias ui-status="sudo systemctl status xiaozhi-admin-ui"
alias ui-logs="journalctl -u xiaozhi-admin-ui -f"
```

```bash
source ~/.bashrc
```

---

## 11. Final checklist

Installation is successful if:

- UI reachable at `http://<SERVER_IP>:<ADMIN_UI_PORT>`
- `/api/health` responds correctly
- dashboard shows no blocking errors
- config reads and writes YAML
- backups are created
- logs are visible
- devices page loads

---

## 12. Troubleshooting

`No module named 'app'`
- running uvicorn outside project root

`Permission denied` on config file
- UI user cannot write `XIAOZHI_CONFIG`

Wrong health status:
- check BACKEND_HOST
- check BACKEND_HEALTH_PORT

Actions not working:
- check XIAOZHI_DIR
- check script paths

Systemd issues:
- check WorkingDirectory
- check EnvironmentFile
- use journalctl

---

## 13. Current limitations

- designed to run on same host as backend
- no built-in authentication
- requires local access to backend repo and config
