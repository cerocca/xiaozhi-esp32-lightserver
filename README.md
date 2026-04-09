# Xiaozhi ESP32 Lightserver

Server-side deployment notes for the `xiaozhi-esp32-lightserver` / `xiaozhi-server` stack.

This repository is documented for a fresh Linux server install with Docker Compose as the primary first-boot path.

## Start Here

- Read `SETUP.md` for the full deployment guide.
- Read `ARCHITECTURE.md` for the port map and runtime flow.
- Use `data/.config.example.yaml` as the starting point for `data/.config.yaml`.

## Core Ports

- `8000` = WebSocket server for ESP32 devices
- `8003` = HTTP server for `/api/health`, OTA, and vision endpoints

Important:

- `http://<SERVER_IP>:8000/` returns plain text `Server is running`
- `http://<SERVER_IP>:8003/api/health` returns JSON
- testing `/api/health` on port `8000` is a mistake and does not validate the HTTP server

Warning:

If you call `/api/health` on port `8000`, you will NOT get JSON.  
This is expected.  
Use port `8003` for HTTP API endpoints.

## SERVER <-> ADMIN UI Integration Contract

Stable integration endpoints:

- health endpoint: `http://<SERVER_HOST>:<HTTP_PORT>/api/health`
- OTA endpoint: `http://<SERVER_HOST>:<HTTP_PORT>/xiaozhi/ota/`
- device WebSocket endpoint: `ws://<SERVER_HOST>:<WS_PORT>/xiaozhi/v1/`

Contract notes:

- Admin UI must use the HTTP port for `/api/health`
- top-level `llm`, `asr`, `tts`, and `device` are backward-compatible
- `details` is additive, and Admin UI may consume `details.*` when present
- `"device": "disconnected"` is normal when no ESP32 device is currently connected
- `/api/health` is the source of truth for backend runtime status

Portability notes:

- service names, script paths, and deployment layout may vary by host
- treat any names or paths in the docs as examples unless explicitly required by the runtime

## Quick Operator Flow

1. Install Docker Engine and the Docker Compose plugin on the Linux server.
2. Clone or copy this repository to `<PROJECT_DIR>`.
3. Copy `data/.config.example.yaml` to `data/.config.yaml`.
4. Replace all placeholders in `data/.config.yaml`.
5. Start the stack with `docker compose up -d`.
6. Verify ports `8000` and `8003` are listening.
7. Check `GET /api/health` on port `8003`.
8. Configure the ESP32 device to use `http://<SERVER_IP>:8003/xiaozhi/ota/`.
9. Confirm the device opens a WebSocket connection to `ws://<SERVER_IP>:8000/xiaozhi/v1/`.

The root `docker-compose.yml` defaults container timezone to `UTC`. Set `TZ` before startup if you want a different local timezone.

## First Verification Commands

```bash
cd <PROJECT_DIR>
docker compose ps
docker compose logs --tail=100
curl -s http://127.0.0.1:8000/
curl -s http://127.0.0.1:8003/api/health
```

Expected:

- `docker compose ps` shows `xiaozhi-esp32-server` as `Up`
- `curl http://127.0.0.1:8000/` returns `Server is running`
- `curl http://127.0.0.1:8003/api/health` returns JSON with top-level `llm`, `asr`, `tts`, and `device`

## Quick Verification (30 Seconds)

```bash
curl http://127.0.0.1:8000/
# expected: Server is running

curl http://127.0.0.1:8003/api/health
# expected: JSON response

curl -s http://127.0.0.1:8003/api/health | jq
# expected: formatted JSON response
```

If `"device": "disconnected"` appears in the health response, that is normal when no ESP32 device is currently connected.

## Documentation Map

- `SETUP.md` - Docker-first Linux install, config, verification, troubleshooting
- `ARCHITECTURE.md` - architecture, ports, and endpoint roles
- `data/.config.example.yaml` - minimal example runtime override file
- `server/README.md` - upstream server project docs, including health endpoint details

## Scope Notes

- Documentation is server-side only.
- Docker Compose is the recommended first-boot deployment path.
- Native Python startup is treated as an advanced/dev scenario, not the main install path.
