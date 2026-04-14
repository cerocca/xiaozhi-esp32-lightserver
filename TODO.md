# TODO - Xiaozhi ESP32 Lightserver

## Next Step
- [ ] Clarify device volume control capability exposure (MCP / IoT descriptors)

## Architecture / Repo Direction
- [ ] Keep the boundary between runtime server and admin tooling clear
- [ ] Evaluate whether the Admin UI should remain standalone or move into the server repo
- [ ] Decide monorepo direction after / together with v0.2.0
- [ ] Review Docker setup: remove dev bind mount and restore production-ready image build

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
