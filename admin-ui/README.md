# Xiaozhi Admin UI

![Status](https://img.shields.io/badge/status-stable-green)
![UI](https://img.shields.io/badge/UI-server--rendered-lightgrey)
![Backend](https://img.shields.io/badge/backend-xiaozhi-blue)
![Health](https://img.shields.io/badge/runtime-health%20API-blue)
![Device](https://img.shields.io/badge/device-ESP32--S3-lightgrey)
![Scope](https://img.shields.io/badge/scope-LAN--only-orange)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Minimal Admin UI to manage and observe a Xiaozhi ESP32 server in a LAN environment.  
For full installation and step-by-step guide see [`SETUP.md`](SETUP.md).

---

## What it does

- Dashboard with runtime status:
  - LLM
  - ASR
  - TTS
  - device (connected / disconnected)

- Real runtime health integration via `/api/health`

- Configuration:
  - LLM
  - ASR
  - TTS

- Read-only modules:
  - VAD
  - Intent
  - Memory

- Logs access (backend and Piper)

- Operational actions:
  - restart
  - logs

**Goal:**
- real debugging  
- simplicity  
- zero overengineering  

---

## Requirements

- A working Xiaozhi-compatible backend (e.g. [xiaozhi-esp32-lightserver](https://github.com/cerocca/xiaozhi-esp32-lightserver) or [xiaozhi-esp32-server](https://github.com/xinnan-tech/xiaozhi-esp32-server) )

- Local access to:
  - backend repository
  - configuration files

- Docker (for backend)
- Piper (optional)

**Note:**  
This UI is primarily tested with `xiaozhi-esp32-lightserver`.  
Other backends exposing `/api/health` may work but are not guaranteed.

---

## Runtime Health

The Admin UI uses the backend `/api/health` endpoint as the single source of truth.

- Top-level fields (`llm`, `asr`, `tts`, `device`) define the primary state  
- `details` are optional and shown only as secondary context  
- The UI never infers state from `details`  
- If the health endpoint is unavailable, the UI shows an `UNKNOWN` state  
- Device `disconnected` is treated as a neutral state, not an error  

This ensures a clear distinction between:
- module errors (backend reachable, component failing)  
- backend unreachable (no reliable runtime data)  

---

## Quick start

```bash
git clone https://github.com/cerocca/xiaozhi-admin-ui.git
cd xiaozhi-admin-ui

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

Edit at least:

```env
XIAOZHI_DIR=...
XIAOZHI_CONFIG=...
```

Run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8088
```

Open:

```text
http://<SERVER_IP>:8088
```

---


## Repository docs

- [`SETUP.md`](SETUP.md) → full installation guide (recommended)  
- [`CHANGELOG.md`](CHANGELOG.md) → versions and changes  

---

## Project status

- `v0.1.5` → stable and usable  
- next → incremental improvements (devices, logs, config UX)  

---

## Philosophy

- Server-rendered (no SPA)  
- No complex JavaScript  
- Real debugging > UI decoration  
- Incremental patches, no massive refactors  
