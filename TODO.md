# TODO — Xiaozhi ESP32 Server

## Priorità alta

- [ ] Tenere allineata la documentazione server con lo stato reale
- [ ] Rifinire la gestione config per provider/modelli lato runtime
- [ ] Capire e correggere il problema orario / offset
- [ ] Fix display (render rotondo vs quadrato)

## Miglioramenti importanti

- [ ] Logging più leggibile
- [ ] Miglior gestione errori Groq (rate limit / fallback)
- [ ] Valutare endpoint o hook più puliti per stato device
- [ ] Ridurre warning/config noise nei log MCP e voiceprint

## Integrazione con tooling admin

- [x] Admin UI separata esistente (`xiaozhi-admin-ui`)
- [ ] Mantenere chiaro il confine tra runtime server e admin tooling
- [ ] Valutare piccoli hook non invasivi che aiutino osservabilità e management

## Evoluzione progetto

- [ ] Supporto LLM locale (Ollama)
- [ ] Memoria conversazione
- [ ] Wake word migliorata
- [ ] Multi-device support più robusto

## Idee future

- [ ] UI display ESP32
- [ ] Integrazione Home Assistant
- [ ] Voice personality custom
- [ ] Supporto nativo Anthropic nel backend Xiaozhi (da valutare solo se la compatibility layer OpenAI risulta limitante)

## Bug / stranezze osservate

- [ ] Device volume non sempre coerente con il valore percepito
- [ ] Possibili reconnect aggressivi
- [ ] Warning MCP / voiceprint da capire e ripulire
- [ ] Verificare se ci sono edge case di restart/config invalidi

## Fatto

- [x] Server su Sibilla
- [x] OTA funzionante
- [x] WebSocket ok
- [x] Groq ASR funzionante
- [x] Groq LLM funzionante
- [x] Piper TTS locale integrato
- [x] Pipeline voce completa funzionante
