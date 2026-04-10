# Changelog

## v0.1.5

Server deployment and packaging refinement release.

### Added
- `.env.example` for first-boot configuration
- custom local Docker image build via root `Dockerfile`
- `docker-compose.dev.yml` to preserve bind-mounted development workflow

### Changed
- default `docker-compose.yml` now builds a local custom image from this repository
- runtime no longer depends on a host-mounted `server/main/xiaozhi-server` source tree
- first-boot setup flow is clearer and more deployment-oriented
- documentation now distinguishes example TTS config from the live runtime TTS profile

### Notes
- mutable runtime data remains host-mounted through `./data`
- the SenseVoice model remains an external mounted asset
- the active live TTS runtime path is profile-based and may differ from example OpenAI TTS snippets in docs


## v0.1.0

Initial stable deployment baseline for this repository.

This project is derived from the `xinnan-tech/xiaozhi-esp32-server` codebase and adapts the upstream server structure for a lighter deployment-focused setup.

### Added
- Docker-first deployment flow
- Clear separation of ports: `8000` for WebSocket, `8003` for HTTP API endpoints
- Backward-compatible `/api/health` top-level contract: `llm`, `asr`, `tts`, `device`
- Additive `/api/health` diagnostic details: `status`, `reason`, `http_status`, `endpoint`
- Quick verification commands and deployment verification flow
- Host-agnostic deployment and setup documentation
- Stable SERVER <-> ADMIN UI integration contract
- `/api/health` documented as the backend runtime source of truth

### Fixed
- Confusion between websocket and HTTP endpoints
- Missing health diagnostics context
- Deployment guidance that depended on host-specific assumptions

### Notes
- External providers used for first boot
- Local model setup documented as advanced scenario
- Plain HTTP requests sent to port `8000` return `Server is running`; this is expected
- Admin UI should use `http://<SERVER_HOST>:<HTTP_PORT>/api/health`
