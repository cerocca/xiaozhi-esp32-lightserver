# TODO – Xiaozhi Admin UI

## For v0.2.0

### 🟡 Medium priority

#### Device runtime details (existing tab enhancement)
Goal: greater runtime visibility

- [ ] Show last seen
- [ ] More detailed WebSocket status
- [ ] Device info (ID, IP, firmware if available)
- [ ] Improve readability of device status in the existing tab

#### More useful logs
Goal: fast debugging without SSH

- [ ] Filter by service (xserver / piper)
- [ ] Select number of lines
- [ ] Error highlighting (server-side or minimal JS)

#### Operations

##### Config
- [ ] Export config (download YAML)
- [ ] Import config (upload YAML)
- [ ] Diff before saving (changes preview)

##### Backup
- [ ] Retention policy (e.g. latest N backups)

---

### 🟢 Low priority / future

#### Device tracking
- [ ] Connection history
- [ ] Basic persistence (lightweight SQLite)

#### Security (LAN-first)
- [ ] Basic Auth for Admin UI
- [ ] Audit log for admin actions (restart/stop/config)
- [ ] Optional reverse proxy (nginx/caddy)
- [ ] Hardening systemd

#### UX / UI polish
- [ ] Improved microcopy
- [ ] Basic responsive layout (mobile)
- [ ] Minor visual alignments

#### Documentation
- [ ] Complete setup from zero (Sibilla)
- [ ] Document:
  - paths
  - permissions
  - systemd services
- [ ] Align docs with real features (no drift)
- [ ] Troubleshooting section based on real cases

---

## ❌ Out of scope (for now)

- Advanced LLM routing
- Continuous auto-refresh / polling
- Architectural refactors
- Firmware / device logic