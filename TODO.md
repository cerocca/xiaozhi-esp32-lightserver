# TODO

## 🚧 In corso / prossimi step

### 🔥 Control plane evolution (priorità alta)
- [ ] Mostrare chiaramente quando è richiesto un restart dopo cambio profilo
- [ ] Aggiungere feedback post-switch (UI → runtime):
  - stato runtime dopo modifica
  - eventuale errore (auth, endpoint, timeout)
- [ ] Rendere esplicita la relazione:
  - config salvata vs runtime effettivo
- [ ] Valutare auto-refresh health dopo cambio profilo

---

### 🧠 Runtime / config consistency
- [ ] Chiarire definitivamente il ruolo di:
  - `runtime.*_profile` (source of truth)
  - `selected_module.*` (legacy compatibility)
- [ ] Ridurre ambiguità nella UI tra config e runtime
- [ ] Verificare comportamento in caso di profilo invalido:
  - credenziali mancanti
  - endpoint errato

---

### 🧹 Technical cleanup (low priority)
- [ ] Valutare impatto di `yaml.safe_dump` su:
  - commenti
  - formattazione
- [ ] Uniformare naming interno (profile_name, provider_id, ecc.)
- [ ] Eventuale cleanup path/script legacy (xserver.sh, piper.sh)

---

### 📦 DX / Packaging
- [ ] Documentare chiaramente avvio Admin UI in README/SETUP
- [ ] Valutare container Docker per admin-ui
- [ ] Setup “one command” per ambiente dev

---

### 🔗 Navigabilità e UX
- [ ] Migliorare navigazione tra:
  - README ↔ Admin UI ↔ Setup
- [ ] Valutare Admin UI come vero “control plane”
- [ ] Ridurre duplicazioni tra AI Stack e pagine modulo

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