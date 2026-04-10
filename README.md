# Xiaozhi ESP32 Lightserver

Deployment-focused server repository for an ESP32 + LLM stack derived from the `xinnan-tech/xiaozhi-esp32-server` codebase.

This repository adapts the upstream server structure for a lighter, Docker-first deployment setup and documents the server as the backend runtime source of truth.

---

## Quick Start

```bash
git clone <REPO_URL> <PROJECT_DIR>
cd <PROJECT_DIR>
cp .env.example .env
cp data/.config.example.yaml data/.config.yaml
# edit .env and data/.config.yaml
docker compose up -d
```

Use Docker Compose as the default first-boot path.

`.env` is the Docker-facing entry point for published ports and timezone.
`data/.config.yaml` remains the server override file for public URLs and provider settings.
`SERVER_HOST` from `.env` is not injected into `data/.config.yaml` yet, so copy the same value into the URLs there.

---

## First Boot Config

Edit only the small set of values below for a normal first install.

```bash
# .env
SERVER_HOST=192.168.1.50
WS_PORT=8000
HTTP_PORT=8003
TZ=Europe/Rome
```

```yaml
# data/.config.yaml
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

`SERVER_HOST` from `.env` is not copied into these URLs automatically yet.
If you change `WS_PORT` or `HTTP_PORT` in `.env`, update these URLs to match.
Keep the default ports unless you intentionally need different published host ports.

For the OpenAI TTS example shown here, `voice` is configurable in `data/.config.yaml`.
Example OpenAI voice: `voice: alloy`
If your live runtime uses a different TTS profile such as `PiperOpenAITTS`, edit that profile's own `voice` field instead.

---

## Quick Verification

These examples assume the default published ports on the same machine.

```bash
curl http://127.0.0.1:8000/
# expected: Server is running

curl http://127.0.0.1:8003/api/health
# expected: JSON response
```

Optional:

```bash
curl -s http://127.0.0.1:8003/api/health | jq
```

If `"device": "disconnected"` appears in the health response, that is normal when no ESP32 device is currently connected.

---

## Ports

- `8000` = WebSocket server for ESP32 devices
- `8003` = HTTP server for `/api/health`, OTA, and other HTTP endpoints

Important:

- `GET /api/health` belongs on port `8003`
- plain HTTP requests to port `8000` return `Server is running`
- if you call `/api/health` on port `8000`, you will not get JSON; this is expected

---

## Runtime Health

Use `http://<SERVER_HOST>:<HTTP_PORT>/api/health` as the backend runtime source of truth.

The top-level `llm`, `asr`, `tts`, and `device` fields are backward-compatible. The `details` object is additive and may be consumed when present.

---

## Documentation

- [SETUP.md](SETUP.md) - full Docker-first deployment, configuration, verification, and troubleshooting guide
- [ARCHITECTURE.md](ARCHITECTURE.md) - architecture, ports, health semantics, and integration surface
- [server/docs/Deployment.md](server/docs/Deployment.md) - short server deployment note and stable integration endpoints

---

## Scope

- server-side documentation only
- Docker-first deployment
- native Python startup is an advanced/dev path, not the main onboarding path
