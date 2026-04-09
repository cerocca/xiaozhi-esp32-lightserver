# Xiaozhi ESP32 Lightserver

Deployment-focused server repository for an ESP32 + LLM stack derived from the `xinnan-tech/xiaozhi-esp32-server` codebase.

This repository adapts the upstream server structure for a lighter, Docker-first deployment setup and documents the server as the backend runtime source of truth.

---

## Quick Start

```bash
git clone <REPO_URL> <PROJECT_DIR>
cd <PROJECT_DIR>
cp data/.config.example.yaml data/.config.yaml
# edit data/.config.yaml
docker compose up -d
```

Use Docker Compose as the default first-boot path.

---

## Quick Verification

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
