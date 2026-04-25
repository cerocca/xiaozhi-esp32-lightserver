# TODO - Xiaozhi ESP32 Lightserver

## Architecture / Repo Direction
- [ ] Keep the boundary between runtime server and admin tooling clear
- [x] Import Admin UI into `admin-ui/` as Phase 1 of the monorepo migration
- [x] Update root docs to present the repository as a monorepo
- [x] Make Admin UI path/config handling work from `admin-ui/` inside the monorepo
- [ ] Make release/docs navigation clearer across root `README`, `admin-ui/README`, `SETUP`, and release notes
- [ ] Evaluate deeper Admin UI to runtime integration and control-plane features
- [ ] Keep `server/main/xiaozhi-server/` path cleanup as optional future work
- [ ] Keep Admin UI containerization optional future work; default Docker/Compose stays server-only
- [ ] Archive/supersede the old standalone `xiaozhi-admin-ui` repo after the README update

## Near-Term Backlog
- [ ] Refine runtime config handling for providers and model profiles
- [ ] Understand and fix the timezone / offset issue

## Known Issues / Runtime Oddities
- [ ] Device volume is not always consistent with perceived loudness
- [ ] Possible aggressive reconnect behavior
- [ ] MCP / voiceprint warnings need review and cleanup
- [ ] Verify restart / invalid-config edge cases
- [ ] Make logging easier to read
- [ ] Improve Groq error handling (rate limit / fallback)

## Later
- [ ] Local LLM support (Ollama)
- [ ] Conversation memory
- [ ] Improved wake word handling
- [ ] More robust multi-device support
- [ ] ESP32 display UI
- [ ] Home Assistant integration (?)
- [ ] Custom voice personality
- [ ] Native Anthropic support in the Xiaozhi backend, only if the OpenAI compatibility layer proves limiting
