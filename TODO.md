# TODO - Xiaozhi ESP32 Lightserver

## Architecture / Repo Direction
- [ ] Keep the boundary between runtime server and admin tooling clear
- [x] Import Admin UI into `admin-ui/` as Phase 1 of the monorepo migration
- [x] Update root docs to present the repository as a monorepo
- [x] Make Admin UI path/config handling work from `admin-ui/` inside the monorepo
- [ ] Align Docker image / Compose packaging as the final monorepo phase
- [ ] Decide whether `server/main/xiaozhi-server/` should be cleaned up to a shorter server path later

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
