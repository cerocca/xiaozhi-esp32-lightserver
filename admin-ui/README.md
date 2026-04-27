# Xiaozhi Admin UI

![Status](https://img.shields.io/badge/status-stable-green)
![UI](https://img.shields.io/badge/UI-server--rendered-lightgrey)
![Backend](https://img.shields.io/badge/backend-xiaozhi-blue)
![Health](https://img.shields.io/badge/runtime-health%20API-blue)
![Device](https://img.shields.io/badge/device-ESP32--S3-lightgrey)
![Scope](https://img.shields.io/badge/scope-LAN--only-orange)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Server-rendered Admin UI for `xiaozhi-esp32-lightserver`.

It lives inside the monorepo under `admin-ui/` and acts as the runtime control plane for the backend in the repository root. The UI reads the shared backend config from `../data/.config.yaml` by default and uses `/api/health` for runtime status.

For full installation details, see [`SETUP.md`](SETUP.md).

## Purpose

Use the Admin UI to:

- inspect runtime health and service status
- edit backend configuration
- manage runtime profiles for LLM, ASR, and TTS
- run isolated LLM, TTS, and ASR tests
- review logs, backups, devices, and restart outcomes

The UI is meant for practical operations on a running Xiaozhi backend, not as a separate standalone product.

## Setup From Zero

```bash
cd admin-ui
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` if needed:

```env
XIAOZHI_DIR=..
XIAOZHI_CONFIG=../data/.config.yaml
```

Notes:

- `XIAOZHI_DIR=..` points to the monorepo root
- `XIAOZHI_CONFIG=../data/.config.yaml` points to the shared backend config
- change those values only if your filesystem layout is different

Run the UI:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8088
```

Open:

```text
http://<server-ip>:8088
```

## Pages

- `Dashboard` shows runtime status cards, restart actions, and the latest health snapshot
- `AI Stack` shows active runtime profiles and entry points for LLM, ASR, and TTS management
- `LLM` manages LLM profiles and includes the runtime prompt test
- `ASR` manages ASR profiles and includes the audio upload transcription test
- `TTS` manages TTS profiles and includes the text-to-audio playback test
- `Config` edits the shared backend YAML configuration
- `Backups` manages saved config snapshots
- `Logs` shows backend and related service logs
- `Devices` shows device visibility and connection-related information

## Runtime Tests

The runtime test actions are isolated checks. They do not automatically restart services.

- `LLM`: prompt input -> response preview
- `TTS`: text input -> generated audio with inline playback
- `ASR`: audio file upload -> transcription preview

These tests are intended to confirm that the currently active runtime profiles are behaving as expected.

## Runtime Health

The UI uses `http://<server-ip>:8003/api/health` as the backend source of truth.

- top-level `llm`, `asr`, `tts`, and `device` fields define the primary state
- `details` is treated as secondary context only
- if the health endpoint is unavailable, the UI shows `UNKNOWN`
- `device=disconnected` is treated as neutral, not as a failure

## Requirements

- a working `xiaozhi-esp32-lightserver` backend or another compatible Xiaozhi backend
- local access to the backend repository and config file
- Python 3 with `venv`
- Docker for the backend deployment flow
- Piper only if your selected TTS profile depends on it

## Repository Docs

- [`SETUP.md`](SETUP.md) for the full Admin UI installation guide
- [`CHANGELOG.md`](CHANGELOG.md) for release notes
