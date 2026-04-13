# Xiaozhi ESP32 Lightserver

[![status](https://img.shields.io/badge/status-stable-2ea44f)](https://github.com/cerocca/xiaozhi-esp32-lightserver)
[![backend](https://img.shields.io/badge/backend-xiaozhi%20lightserver-0a7ea4)](https://github.com/cerocca/xiaozhi-esp32-lightserver)
[![runtime](https://img.shields.io/badge/runtime-health%20API-4c9f38)](https://github.com/cerocca/xiaozhi-esp32-lightserver/blob/main/SETUP.md)
[![device](https://img.shields.io/badge/device-ESP32--S3%20%2F%20xiaozhi-555555)](https://github.com/xinnan-tech/xiaozhi-esp32-server)
[![deploy](https://img.shields.io/badge/deploy-Docker%20image-2496ED?logo=docker&logoColor=white)](https://github.com/cerocca/xiaozhi-esp32-lightserver/blob/main/SETUP.md)
[![scope](https://img.shields.io/badge/scope-self--hosted%20%2F%20LAN--first-6f42c1)](https://github.com/cerocca/xiaozhi-esp32-lightserver)

Deployment-focused server repository for an ESP32 device (xiaozhi based) + LLM stack, derived from the upstream project:

👉 https://github.com/xinnan-tech/xiaozhi-esp32-server

This repository adapts the upstream server structure for a lighter, Docker-first deployment setup and treats the server as the backend runtime source of truth.

👉 Companion Admin UI (health, logs, device status, and runtime status views powered by `/api/health`) available at  
[https://github.com/cerocca/xiaozhi-admin-ui](https://github.com/cerocca/xiaozhi-admin-ui)

---

## What this repo is

This is a **deployment-oriented backend** for ESP32 voice devices.

- Docker-first setup  
- Minimal configuration surface  
- Runtime-driven (`/api/health`)  
- Designed for stability, not experimentation  

> This is not a generic LLM server.  
> It is the runtime backend for ESP32-based voice devices.

---

## Quick Start

```bash
git clone https://github.com/cerocca/xiaozhi-esp32-lightserver.git
cd xiaozhi-esp32-lightserver

cp .env.example .env
cp data/.config.example.yaml data/.config.yaml

# edit .env
# edit data/.config.yaml

docker compose up -d
```

👉 See **[SETUP.md](SETUP.md)** for full configuration and troubleshooting.

---

## What The Docker Image Contains

The default `docker compose` flow builds a custom image from this repository.

- The image contains the server code and its packaged runtime environment.
- Your runtime data stays external in `./data`.
- Model assets stay external unless you provide them separately on the host.
- Remote/API-based providers still require valid URLs, credentials, and models in `data/.config.yaml`.

This means the image is not a full self-contained AI stack by itself. If you choose local components such as host-provided ASR models or Piper voices, those assets still need to exist outside the image and be mounted or otherwise made available at runtime.

---

## First Boot Config

### `.env`

```bash
SERVER_HOST=192.168.1.50
WS_PORT=8000
HTTP_PORT=8003
TZ=Europe/Rome
```

### `data/.config.yaml`

```yaml
server:
  websocket: ws://192.168.1.50:8000/xiaozhi/v1/
  vision_explain: http://192.168.1.50:8003/mcp/vision/explain

ASR:
  openai_asr:
    api_key: sk-...

LLM:
  openai_llm:
    api_key: sk-...

TTS:
  openai_tts:
    api_key: sk-...
    voice: alloy
```

⚠️ `SERVER_HOST` is **not injected automatically** into config.  
Keep `.env` and `data/.config.yaml` aligned manually.

---

## Ports

Default exposed ports:

- `8000` → WebSocket (device connection)  
- `8003` → HTTP API (`/api/health`, OTA, etc.)

If you change ports in `.env`, update URLs in `data/.config.yaml`.

---

## Runtime Architecture

### Top-level (`/api/health`)

- `llm`
- `asr`
- `tts`
- `device`

### Details

- provider diagnostics  
- endpoint checks  
- HTTP status mapping  

### Principles

- top-level = source of truth  
- details = context only  
- `device=disconnected` = normal state (no error)

---

## TTS Configuration

The `voice` parameter depends on the active runtime profile.

### OpenAI example

```yaml
TTS:
  openai_tts:
    voice: alloy
```

### Live runtime example (Piper)

```yaml
TTS:
  PiperOpenAITTS:
    voice: riccardo
```

👉 Always edit the **active profile**, not the example one.

---

## Docker Setup

Build + run:

```bash
docker compose build
docker compose up -d
```

### Runtime mounts

- `./data` → config + runtime state  
- `./models/...` → host-provided local model assets, when used  

### Read this before first boot

- The built image already includes the server code from this repository.
- `data/.config.yaml` is still external and controls the live runtime behavior.
- Local model files and similar assets are not automatically bundled into the image.
- Some deployments use remote providers for LLM, ASR, or TTS, so those API endpoints and credentials must still be configured correctly.
- Some local components, including Piper or local speech/model paths, may still require host-side provisioning depending on the profile you activate.

### Dev mode (optional)

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

---

## Quick Verification

After startup, verify that the server is running correctly:

```bash
curl http://127.0.0.1:8000/
# expected: Server is running

curl http://127.0.0.1:8003/api/health | jq
```

Expected result:

- `llm: ok`  
- `asr: ok`  
- `tts: ok`  
- `device: disconnected` (until ESP32 connects)

👉 This confirms:
- server is up  
- providers are reachable  
- TTS path is working  

---

## Project Structure

```
.
├── data/                      # runtime config (mounted)
├── models/                    # optional host-provided local models
├── server/main/xiaozhi-server # upstream server code
├── Dockerfile                 # image packaging
├── docker-compose.yml         # runtime
├── docker-compose.dev.yml     # dev override
├── README.md
├── SETUP.md
```

---

## Notes

- `.env` = Docker/runtime exposure  
- `data/.config.yaml` = actual server behavior  
- local model assets remain external when your chosen runtime needs them
- keep them aligned manually  
- rebuild required after server code changes  

---

## Credits

Based on:  
https://github.com/xinnan-tech/xiaozhi-esp32-server
