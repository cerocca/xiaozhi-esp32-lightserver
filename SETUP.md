# Server Deployment Guide

Docker Compose is the recommended first-boot path for a fresh Linux server.

This guide is written for a careful operator who wants the highest chance of a clean first install without reading source code.

## 1. What You Are Deploying

The server runtime exposes two separate ports:

- `8000` = WebSocket server for ESP32 devices
- `8003` = HTTP server for `/api/health`, OTA, and vision endpoints

Important:

- `8000` answers plain HTTP requests with `Server is running`
- `8003` serves JSON endpoints
- `GET /api/health` must be tested on port `8003`, not `8000`

Warning:

If you call `/api/health` on port `8000`, you will NOT get JSON.  
This is expected.  
Use port `8003` for HTTP API endpoints.

## 2. Prerequisites

Required:

- Linux server with shell access
- Docker Engine
- Docker Compose plugin
- outbound network access for the external LLM, ASR, and TTS providers you configure
- valid provider credentials

Recommended packages:

```bash
sudo apt update
sudo apt install -y git curl ca-certificates docker.io docker-compose-plugin
sudo usermod -aG docker "$USER"
```

After `usermod`, start a new shell session before continuing.

Verify:

```bash
docker --version
docker compose version
curl --version
```

## 3. Quickstart

Run these steps in order:

1. Clone or copy the repository to `<PROJECT_DIR>`.
2. Create `data/.config.yaml` from `data/.config.example.yaml`.
3. Replace every placeholder in `data/.config.yaml`.
4. Start the server with `docker compose up -d`.
5. Check container status and logs.
6. Verify port `8000` and port `8003`.
7. Verify `GET /api/health` on port `8003`.
8. Configure the ESP32 device to use `http://<SERVER_HOST>:8003/xiaozhi/ota/`.
9. Confirm the device connects to `ws://<SERVER_HOST>:8000/xiaozhi/v1/`.

### Stable Integration Contract

Use these endpoints as the stable SERVER <-> ADMIN UI integration surface:

- health endpoint: `http://<SERVER_HOST>:<HTTP_PORT>/api/health`
- OTA endpoint: `http://<SERVER_HOST>:<HTTP_PORT>/xiaozhi/ota/`
- device WebSocket endpoint: `ws://<SERVER_HOST>:<WS_PORT>/xiaozhi/v1/`

Important:

- Admin UI must use the HTTP port for `/api/health`
- top-level `llm`, `asr`, `tts`, and `device` are backward-compatible
- `details` is additive, and UI consumers may read `details.*` when present
- HTTP status mapping rules are defined in the health endpoint section below
- `"device": "disconnected"` is normal when no ESP32 device is currently connected

## 4. Install the Project

```bash
cd /opt
git clone <REPO_URL> xiaozhi-esp32-lightserver
cd /opt/xiaozhi-esp32-lightserver
mkdir -p data
cp data/.config.example.yaml data/.config.yaml
```

Replace:

- `<REPO_URL>` with your repository URL
- `/opt/xiaozhi-esp32-lightserver` with your preferred `<PROJECT_DIR>`

Portability note:

- service names, script paths, and deployment layout may vary by host
- examples in this guide use placeholders and should not be treated as required local names

## 5. Prepare the Runtime Config

### 5.1 Files That Matter

Use these files:

- `data/.config.yaml` = real deployment config
- `data/.config.example.yaml` = versioned example
- `server/main/xiaozhi-server/config.yaml` = shipped defaults, normally not edited for deployment

Do not put deployment secrets into version-controlled files.

### 5.2 Mandatory Values

At minimum, set:

- `server.websocket`
- `server.vision_explain`
- `selected_module.LLM`
- `selected_module.ASR`
- `selected_module.TTS`
- `selected_module.Intent`
- `runtime.llm_profile`
- `runtime.asr_profile`
- `runtime.tts_profile`
- LLM provider URL, API key, and model
- ASR provider URL, API key, and model
- TTS provider URL, API key, and voice/model

### 5.3 Optional Values

Optional for first boot:

- `server.auth.enabled`
- `server.auth_key`
- `Memory`
- `VLLM`
- `voiceprint`
- `plugins`
- `manager-api`

### 5.4 Minimal First-Boot Example

This example keeps the deployment path simple by using external/API-based providers.

```yaml
server:
  websocket: ws://<SERVER_HOST>:8000/xiaozhi/v1/
  vision_explain: http://<SERVER_HOST>:8003/mcp/vision/explain

selected_module:
  VAD: SileroVAD
  ASR: OpenaiASR
  LLM: AliLLM
  TTS: OpenAITTS
  Memory: nomem
  Intent: nointent

runtime:
  asr_profile: openai_asr
  llm_profile: openai_llm
  tts_profile: openai_tts

Intent:
  nointent:
    type: nointent

Memory:
  nomem:
    type: nomem

ASR:
  OpenaiASR:
    type: openai
  openai_asr:
    type: openai
    api_key: <OPENAI_API_KEY>
    base_url: https://api.openai.com/v1/audio/transcriptions
    model_name: gpt-4o-mini-transcribe
    output_dir: tmp/

LLM:
  AliLLM:
    type: openai
  openai_llm:
    type: openai
    api_key: <OPENAI_API_KEY>
    base_url: https://api.openai.com/v1
    model_name: gpt-4o-mini

TTS:
  OpenAITTS:
    type: openai
  openai_tts:
    type: openai
    api_key: <OPENAI_API_KEY>
    api_url: https://api.openai.com/v1/audio/speech
    model: tts-1
    voice: alloy
    speed: 1
    output_dir: tmp/
```

Notes:

- You may use any OpenAI-compatible provider instead of the example above.
- Keep the logical module entries such as `OpenaiASR`, `AliLLM`, and `OpenAITTS`.
- Keep the active profile names aligned with `runtime.*_profile`.

### 5.5 Common Config Mistakes

- Wrong file path: use `data/.config.yaml`
- Wrong port in `server.websocket`: must point to `8000`
- Wrong health test target: `GET /api/health` belongs on `8003`
- Mismatched profile names: `runtime.llm_profile` must exist under `LLM`, and the same for `ASR` and `TTS`
- Typo in `selected_module.Intent`: a bad name can crash startup

## 6. Start the Server

```bash
cd <PROJECT_DIR>
docker compose up -d
```

Optional:

- set `TZ` in the shell before startup if you want container logs in your local timezone
- if unset, the root Compose file defaults to `UTC`

Check status:

```bash
cd <PROJECT_DIR>
docker compose ps
docker ps --filter name=xiaozhi-esp32-server
```

Check logs:

```bash
cd <PROJECT_DIR>
docker compose logs --tail=100
docker compose logs -f --tail=100
```

Restart:

```bash
cd <PROJECT_DIR>
docker compose restart
```

Stop:

```bash
cd <PROJECT_DIR>
docker compose down
```

## 7. Verify the Deployment

### 7.0 Quick Verification (30 Seconds)

```bash
curl http://127.0.0.1:8000/
# expected: Server is running

curl http://127.0.0.1:8003/api/health
# expected: JSON response

curl -s http://127.0.0.1:8003/api/health | jq
# expected: formatted JSON response
```

### 7.1 Container Check

```bash
cd <PROJECT_DIR>
docker compose ps
```

Expected:

- service `xiaozhi-esp32-server` is `Up`

### 7.2 Port Check

```bash
ss -ltnp | grep -E ':8000|:8003'
```

Expected:

- one listener on `8000`
- one listener on `8003`

### 7.3 WebSocket Port Sanity Check

```bash
curl -s http://127.0.0.1:8000/
```

Expected:

```text
Server is running
```

This confirms the WebSocket listener is reachable for plain HTTP, but it does not validate the health API.

### 7.4 HTTP Health Check

```bash
curl -s http://127.0.0.1:8003/api/health
```

Expected shape:

```json
{
  "llm": "ok",
  "asr": "ok",
  "tts": "ok",
  "device": "disconnected",
  "details": {
    "llm": {
      "status": "ok",
      "reason": "ok",
      "http_status": 200,
      "endpoint": "https://api.openai.com/v1/models"
    },
    "asr": {
      "status": "ok",
      "reason": "ok",
      "http_status": 405,
      "endpoint": "https://api.openai.com/v1/audio/transcriptions"
    },
    "tts": {
      "status": "ok",
      "reason": "ok",
      "http_status": 405,
      "endpoint": "https://api.openai.com/v1/audio/speech"
    },
    "device": {
      "status": "disconnected",
      "reason": "disconnected",
      "last_seen": null,
      "connection_duration": null
    }
  }
}
```

Important:

- top-level keys are backward-compatible
- `details` is additive
- Admin UI may safely consume `details.*` when present
- `"device": "disconnected"` is normal when no ESP32 device is currently connected
- if UI-side local checks disagree with `/api/health`, treat `/api/health` as the source of truth for backend runtime status

### 7.5 OTA Check

```bash
curl -i http://127.0.0.1:8003/xiaozhi/ota/
```

Use the exact OTA URL on the ESP32 device:

```text
http://<SERVER_HOST>:8003/xiaozhi/ota/
```

### 7.6 Device Connection Check

After the device is configured, watch logs:

```bash
cd <PROJECT_DIR>
docker compose logs -f --tail=100
```

Typical connection indicators include:

- OTA request entries
- hello/listen/mcp message handling
- ASR text recognition
- successful TTS generation

After a successful WebSocket connection, `device` in `/api/health` should switch from `disconnected` to `connected`.

## 8. Health Endpoint Semantics

### 8.1 Top-Level Contract

These keys remain stable for existing callers:

```json
{
  "llm": "ok",
  "asr": "ok",
  "tts": "ok",
  "device": "connected"
}
```

### 8.2 Additive Details Object

`details.llm`, `details.asr`, and `details.tts` contain:

- `status`: `ok` or `error`
- `reason`: `ok`, `timeout`, `connection_error`, `auth_error`, or `http_error`
- `http_status`: HTTP status code if a response was received, else `null`
- `endpoint`: final URL probed by the health check

`details.device` contains:

- `status`: `connected` or `disconnected`
- `reason`: `connected` or `disconnected`
- `last_seen`: currently `null`
- `connection_duration`: currently `null`

### 8.3 Status Mapping Rules

- timeout -> `timeout`
- connection errors or request exceptions before response -> `connection_error`
- HTTP `401` or `403` -> `auth_error`
- HTTP `>=500` -> `http_error`
- any other HTTP `<500` -> `ok`

Practical consequence:

- ASR can show `http_status: 404` or `405` and still be `ok`
- TTS may probe `/health` first and then fall back to the base URL
- `details.tts` reports only the final probe result

## 9. Troubleshooting

### 9.1 `/api/health` Returns Plain Text

Cause:

- you hit port `8000` instead of `8003`

If you call `/api/health` on port `8000`, you will NOT get JSON.  
This is expected.  
Use port `8003` for HTTP API endpoints.

Fix:

```bash
curl -s http://127.0.0.1:8003/api/health
```

### 9.2 `curl http://127.0.0.1:8000/` Shows `Server is running`

This is expected.

It only proves the WebSocket listener is present. Use port `8003` for JSON checks.

### 9.3 Health Shows `device: disconnected`

Meaning:

- no device is currently connected over WebSocket

This is not a provider failure by itself.

### 9.4 Health Shows `auth_error`

Meaning:

- the upstream provider returned `401` or `403`

Check:

- API key
- endpoint URL
- provider account/project configuration

### 9.5 Health Shows `connection_error`

Check:

- DNS resolution on the server
- outbound firewall rules
- proxy settings if your provider requires them
- wrong base URL or typo in host name

### 9.6 Health Shows `http_error`

Meaning:

- upstream provider returned `5xx`

Check:

- provider service status
- temporary outage or overloaded upstream
- wrong route on a self-hosted compatible API

### 9.7 ASR Shows `404` but Status Is Still `ok`

This can be expected with the current health mapping when the provider endpoint responds with an HTTP code below `500`.

Do not treat this as a failure by itself. Validate real speech flow with a device test.

### 9.8 Container Starts but Voice Flow Fails

Check:

- `server.websocket` points to the real reachable server address
- the device OTA URL uses port `8003`
- the device WebSocket target uses port `8000`
- provider model names are valid
- `runtime.llm_profile`, `runtime.asr_profile`, and `runtime.tts_profile` reference existing profile names

## 10. Advanced / Dev Appendix

Native Python startup exists in the upstream project, but it is not the recommended first deployment path for a new Linux server.

Use it only when you are:

- developing locally
- debugging the runtime outside Docker
- intentionally managing Python dependencies yourself
