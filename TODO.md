# TODO

## 🚧 In corso / prossimi step

### 🔥 Control plane evolution (priorità alta)

- [ ] Valutare auto-refresh health dopo switch/restart
- [ ] Ridurre ulteriormente ambiguità tra:
  - config salvata
  - runtime attivo

---

### 🧠 Profile validation
- [ ] Verificare comportamento in caso di profilo invalido:
  - credenziali mancanti
  - endpoint errato
- [ ] Validare meglio i profili prima dello switch runtime
- [ ] Rendere piu esplicita la relazione tra config salvata e runtime effettivo

---

### 🧪 Component test actions
- [ ] Aggiungere test action per:
  - ASR (basic transcription test)
- [ ] Migliorare output test:
  - distinguere meglio error types (auth, timeout, http)
- [ ] Coprire i flussi save / switch / restart con test action essenziali
- [ ] Verificare casi health/error nelle pagine modulo
---

### 🧹 Runtime / config cleanup
- [ ] Chiarire definitivamente il ruolo di:
  - `runtime.*_profile` (source of truth)
  - `selected_module.*` (legacy compatibility)
- [ ] Ridurre ambiguita nella UI tra config e runtime
- [ ] Valutare impatto di `yaml.safe_dump` su:
  - commenti
  - formattazione
- [ ] Uniformare naming interno (profile_name, provider_id, ecc.)
- [ ] Eventuale cleanup path/script legacy (xserver.sh, piper.sh)

---

### 🔗 Docs / release navigation
- [ ] Migliorare navigazione tra:
  - README ↔ Admin UI ↔ Setup
- [ ] Rendere piu chiaro il percorso release/changelog per micro-fix docs-only
- [ ] Ridurre duplicazioni tra README, changelog e note operative

---

## 📌 Fatto recentemente (v0.2.1)

- [x] AI Stack come entry point per Runtime Profiles
- [x] Visualizzazione:
  - `runtime.llm_profile`
  - `runtime.asr_profile`
  - `runtime.tts_profile`
- [x] Overview per modulo (LLM / ASR / TTS):
  - profilo attivo
  - numero profili disponibili
  - stato runtime
- [x] Miglioramento UX pagine LLM / ASR / TTS:
  - distinzione tra save / activate / restart
- [x] Fix robustezza template (`health_status` opzionale)
