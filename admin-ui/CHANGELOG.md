# Changelog

All relevant Admin UI changes are recorded here.

## [Unreleased]

---

## [0.1.5]

### Improvements
- UI Health UX completed:
  - clear distinction between module error and backend unreachable
  - UNKNOWN state when health is unavailable
  - device disconnected is now neutral (not an error)
  - details displayed as secondary context only

### Fixes
- restored backward compatibility in health fallback payload
- ensured top-level health fields are always present (llm/asr/tts/device)

---

## [0.1.1]

- Improved Admin UI portability through centralized configuration.
- Introduced `.env.example` for simplified setup.
- Removed hardcoded paths and used settings/env consistently.
- Improved documentation (README and SETUP) for installation from zero.
- Fixed wrapper scripts (`xserver.sh`, `piper.sh`) to support environment variables.
- Improved handling of internal paths (backup, log, script) relative to the project root.

---

## [0.1.0]

- First stable milestone of the server-rendered Admin UI.
- Initial dashboard with main service status and quick access to logs.
- Introduced the AI Stack section to organize the available AI modules.
- Basic LLM configuration with main profile management.
- Core operational pages for config editor, backups, logs, and devices.
- Initial management of Xiaozhi server, Piper, and runtime configuration.
- Added full CRUD management for ASR and TTS profiles.
- Improved the AI Stack page with a more consistent layout and better aligned cards.
- Initial integration of runtime health from the Xiaozhi backend.
- Added runtime device visibility in the UI.
- Refined the dashboard with more consistent restart/stop/log actions.
- Improved the TTS configuration experience with dropdown `voice` support for providers like Piper.