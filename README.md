# Xiaozhi ESP32 Lightserver

Deployment-focused server repository for an ESP32 device (xiaozhi based) + LLM stack, derived from the upstream project:

https://github.com/xinnan-tech/xiaozhi-esp32-server

This repository adapts the upstream server structure for a lighter, Docker-first deployment setup and treats the server as the backend runtime source of truth.

Companion Admin UI (health, logs, device status):
https://github.com/cerocca/xiaozhi-admin-ui

---

## What this repo is

This is a deployment-oriented backend for ESP32 voice devices.

- Docker-first setup
- Minimal configuration surface
- Runtime-driven (via /api/health)
- Designed for stability, not experimentation

This is not a generic LLM server.
It is the runtime backend for ESP32-based voice devices.

---

## Quick Start

git clone https://github.com/cerocca/xiaozhi-esp32-lightserver.git
cd xiaozhi-esp32-lightserver

cp .env.example .env
cp data/.config.example.yaml data/.config.yaml

# edit .env
# edit data/.config.yaml

docker compose up -d

For full setup details, see SETUP.md

---

## First Boot (minimal config)

.env

SERVER_HOST=192.168.1.50
WS_PORT=8000
HTTP_PORT=8003
TZ=Europe/Rome

data/.config.yaml

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

---

## Runtime Architecture

Top-level status (/api/health):
- llm
- asr
- tts
- device

Details:
- provider-level diagnostics
- endpoint checks
- HTTP status mapping

Principles:
- top-level = source of truth
- details = context only
- device=disconnected is neutral

---

## TTS Configuration

Example (OpenAI):

TTS:
  openai_tts:
    voice: alloy

Live example (Piper):

TTS:
  PiperOpenAITTS:
    voice: riccardo

Always edit the active profile.

---

## Docker Setup

docker compose build
docker compose up -d

---

## Verification

curl http://127.0.0.1:8000/
curl http://127.0.0.1:8003/api/health

---

## Project Structure

data/
models/
server/main/xiaozhi-server
Dockerfile
docker-compose.yml
docker-compose.dev.yml
README.md
SETUP.md
