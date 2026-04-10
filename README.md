# Xiaozhi ESP32 Lightserver

Deployment-focused server repository for an ESP32 device (xiaozhi based) + LLM stack, derived from the upstream project:

👉 https://github.com/xinnan-tech/xiaozhi-esp32-server

This repository adapts the upstream server structure for a lighter, Docker-first deployment setup and treats the server as the backend runtime source of truth.

👉 Companion Admin UI (health, logs, device status) available at  
https://github.com/cerocca/xiaozhi-admin-ui

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
- `./models/...` → ASR model  

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
├── models/                    # ASR models (mounted)
├── server/main/xiaozhi-server # upstream server code
├── Dockerfile                # image packaging
├── docker-compose.yml        # runtime
├── docker-compose.dev.yml    # dev override
├── README.md
├── SETUP.md
```

---

## Notes

- `.env` = Docker/runtime exposure  
- `data/.config.yaml` = actual server behavior  
- keep them aligned manually  
- rebuild required after server code changes  

---

## Credits

Based on:  
https://github.com/xinnan-tech/xiaozhi-esp32-server
