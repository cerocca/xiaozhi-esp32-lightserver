# TODO - Xiaozhi ESP32 Server

## High Priority

- [ ] Keep the server documentation aligned with the real runtime state
- [ ] Refine runtime config handling for providers and model profiles
- [ ] Understand and fix the timezone / offset issue
- [ ] Fix display rendering differences (round vs square)

## Important Improvements

- [ ] Make logging easier to read
- [ ] Improve Groq error handling (rate limit / fallback)
- [ ] Evaluate cleaner endpoints or hooks for device state
- [ ] Reduce MCP and voiceprint warning/config noise in logs

## Admin Tooling Integration

- [x] Separate Admin UI project exists (`xiaozhi-admin-ui`)
- [ ] Keep the boundary between runtime server and admin tooling clear
- [ ] Evaluate small non-invasive hooks that improve observability and management

## Project Evolution

- [ ] Local LLM support (Ollama)
- [ ] Conversation memory
- [ ] Improved wake word handling
- [ ] More robust multi-device support

## Future Ideas

- [ ] ESP32 display UI
- [ ] Home Assistant integration
- [ ] Custom voice personality
- [ ] Native Anthropic support in the Xiaozhi backend, only if the OpenAI compatibility layer proves limiting

## Bugs / Observed Oddities

- [ ] Device volume is not always consistent with perceived loudness
- [ ] Possible aggressive reconnect behavior
- [ ] MCP / voiceprint warnings need review and cleanup
- [ ] Verify restart/config-invalid edge cases

## Done

- [x] Server running
- [x] OTA working
- [x] WebSocket working
- [x] Groq ASR working
- [x] Groq LLM working
- [x] Local Piper TTS integrated
- [x] End-to-end voice pipeline working
