# Changelog

All relevant Admin UI changes are recorded here.

## [Unreleased]

### 🛠 Fixed
- Updated Admin UI metadata after monorepo migration
- Simplified Admin UI header subtitle
- Made switch feedback more consistent across modules (LLM / ASR / TTS)
- Reduced ambiguity between configuration saved and runtime state

### ✨ Added
- Improved post-switch feedback across LLM / ASR / TTS pages:
  - explicit display of selected runtime profile
  - clear indication that `.config.yaml` was updated via `runtime.*_profile`
  - reminder that restart may be required for changes to take effect
  - clarification that `/api/health` is operational context only
  - Added minimal "Test LLM" action in Admin UI:
		- executes a real OpenAI-compatible completion using the active runtime profile
		- shows HTTP status, endpoint, and short reply preview
		- provides a direct operational check independent from `/api/health`

### 🔄 Changed
- Improved restart feedback pages:
  - explicit success / error messaging
  - direct links to relevant logs
  - quick access to AI Stack
  - clearer guidance on how to verify runtime state


## [0.2.1] - 2026-04-25

### ✨ Added
- AI Stack page now acts as entry point for Runtime Profiles
- Display of:
  - `runtime.llm_profile`
  - `runtime.asr_profile`
  - `runtime.tts_profile`
- Per-module overview (LLM / ASR / TTS):
  - active profile
  - available profiles count
  - runtime health badge
- Direct navigation actions:
  - “Manage LLM”
  - “Manage ASR”
  - “Manage TTS”

### 🔄 Changed
- Improved clarity of runtime vs configuration in LLM / ASR / TTS pages
- Clearer distinction between:
  - saving a profile
  - switching active runtime profile
  - restart requirement for applying changes
- AI Stack layout reorganized to prioritize runtime visibility

### 🛠 Fixed
- Prevented template crashes when `health_status` is missing
- Made health rendering resilient across all module pages (`llm`, `asr`, `tts`)

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

## [0.1.1]
- Improved Admin UI portability through centralized configuration.
- Introduced .env.example for simplified setup.
- Removed hardcoded paths and used settings/env consistently.
- Improved documentation (README and SETUP) for installation from zero.
- Fixed wrapper scripts (xserver.sh, piper.sh) to support environment variables.
- Improved handling of internal paths (backup, log, script) relative to the project root.

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
- Improved the TTS configuration experience with dropdown voice support for providers like Piper.
