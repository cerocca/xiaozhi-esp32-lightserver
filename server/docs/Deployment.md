# Server Deployment Note

For a fresh Linux server deployment of the server runtime, use the repository root guide:

- `SETUP.md` for the Docker Compose installation flow
- `ARCHITECTURE.md` for the port and endpoint map
- `data/.config.example.yaml` as the minimal starting config

The recommended operator path is:

1. Docker Compose first
2. external/API-based providers for first boot
3. explicit verification of:
   - port `8000` for the WebSocket listener
   - port `8003` for HTTP endpoints
   - `GET /api/health` on port `8003`

Important:

- port `8000` is the WebSocket server and answers plain HTTP with `Server is running`
- port `8003` is the HTTP server and exposes `/api/health`, OTA, and vision endpoints
- testing `/api/health` on port `8000` is a false check

Warning:

If you call `/api/health` on port `8000`, you will NOT get JSON.  
This is expected.  
Use port `8003` for HTTP API endpoints.

Stable integration endpoints:

- health endpoint: `http://<SERVER_HOST>:<HTTP_PORT>/api/health`
- OTA endpoint: `http://<SERVER_HOST>:<HTTP_PORT>/xiaozhi/ota/`
- device WebSocket endpoint: `ws://<SERVER_HOST>:<WS_PORT>/xiaozhi/v1/`

Portability note:

- service names, script paths, and deployment layout may vary by host
- use placeholders such as `<SERVER_HOST>`, `<HTTP_PORT>`, and `<WS_PORT>` in deployment examples

Native Python startup and more specialized deployment variants should be treated as advanced scenarios, not as the default first-install path.
