# Architecture

## Overview

Runtime flow:

`ESP32 device -> WebSocket server -> ASR -> LLM -> TTS -> audio back to device`

The server process exposes two different network services:

- a WebSocket service for device sessions
- an HTTP service for operator checks and auxiliary endpoints

## Port Map

### Port 8000

- Protocol: WebSocket
- Purpose: ESP32 device communication
- Main path: `/xiaozhi/v1/`
- Behavior on plain HTTP requests: returns `Server is running`

This is not the health API port.

### Port 8003

- Protocol: HTTP
- Purpose: operator-facing HTTP endpoints
- Main endpoints:
  - `GET /api/health`
  - `GET /xiaozhi/ota/`
  - `POST /xiaozhi/ota/`
  - `GET /mcp/vision/explain`
  - `POST /mcp/vision/explain`

This is the port you must use for JSON health checks.

## Common Port Mistake

These two commands are not equivalent:

```bash
curl http://<SERVER_IP>:8000/api/health
curl http://<SERVER_IP>:8003/api/health
```

What happens:

- on `8000`, the request reaches the WebSocket listener and you do not get the JSON health payload
- on `8003`, the request reaches the HTTP server and returns the health JSON

Warning:

If you call `/api/health` on port `8000`, you will NOT get JSON.  
This is expected.  
Use port `8003` for HTTP API endpoints.

For a quick socket-level sanity check, use:

```bash
curl http://<SERVER_IP>:8000/
```

Expected response:

```text
Server is running
```

## Runtime Configuration Model

The server loads:

- base defaults from `server/main/xiaozhi-server/config.yaml`
- local runtime overrides from `data/.config.yaml`

Recommended operator workflow:

- do not edit `server/main/xiaozhi-server/config.yaml` for normal deployments
- keep deployment-specific values in `data/.config.yaml`
- version `data/.config.example.yaml`
- never commit secrets from `data/.config.yaml`

## Minimum External Provider Layout

For first boot, use external/API-based providers and a small override file:

- `selected_module.*` chooses the logical module/driver
- `runtime.*_profile` chooses the active provider profile
- `LLM`, `ASR`, and `TTS` contain the named provider configs

This keeps the deployment path simple and avoids requiring local model downloads for the first successful install.

## Health Endpoint Summary

`GET /api/health` returns:

- backward-compatible top-level keys:
  - `llm`
  - `asr`
  - `tts`
  - `device`
- additive `details` object for diagnostics

Meaning of `device`:

- `connected` means at least one device currently has an active WebSocket session
- `disconnected` means no device is currently connected
- `"device": "disconnected"` is normal when no ESP32 device is currently connected

## Operator View

For a fresh deployment, the important mental model is:

1. port `8000` proves the WebSocket listener is up
2. port `8003` proves the HTTP endpoints are up
3. `/api/health` validates provider reachability and current device connection state
4. OTA points devices at the WebSocket endpoint used at runtime
