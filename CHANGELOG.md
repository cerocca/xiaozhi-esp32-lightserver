# Changelog

## v0.1.0

Initial stable deployment version.

### Added
- Docker-first deployment flow
- Clear separation of ports (8000 websocket, 8003 HTTP)
- /api/health diagnostic details (status, reason, http_status, endpoint)
- Quick verification commands
- Deployment and setup documentation

### Fixed
- Confusion between websocket and HTTP endpoints
- Missing health diagnostics context

### Notes
- External providers used for first boot
- Local model setup documented as advanced scenario

