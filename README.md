# Xiaozhi ESP32 Server (Sibilla)

![Status](https://img.shields.io/badge/status-working-green)
![ASR](https://img.shields.io/badge/ASR-Groq-blue)
![LLM](https://img.shields.io/badge/LLM-Groq-blue)
![TTS](https://img.shields.io/badge/TTS-Piper-orange)
![Device](https://img.shields.io/badge/device-ESP32--S3-lightgrey)

Server vocale locale/LAN per device ESP32-S3 XiaoZhi-like, con pipeline completa:

**ESP32 → Xiaozhi Server → Groq (ASR + LLM) → Piper locale (TTS) → audio sul device**

## Stato attuale verificato

Funzionano:

- OTA del device
- WebSocket verso il server
- ASR via Groq
- LLM via Groq
- TTS via Piper locale esposto come endpoint OpenAI-compatible
- riproduzione audio sul device
- controllo volume del device via voce

## Setup di riferimento

Host usato nella documentazione:

- host Linux: `Sibilla`
- IP LAN: `192.168.1.69`

Percorsi usati:

- repo server: `/home/ciru/xiaozhi-esp32-server`
- config runtime: `/home/ciru/xiaozhi-esp32-server/data/.config.yaml`
- config example da versionare: `/home/ciru/xiaozhi-esp32-server/data/.config.example.yaml`
- Piper API: servizio `piper-api`
- Admin UI opzionale: `/home/ciru/xiaozhi-admin-ui`

## Endpoints usati nel setup documentato

- OTA: `http://192.168.1.69:8003/xiaozhi/ota/`
- WebSocket: `ws://192.168.1.69:8000/xiaozhi/v1/`
- Piper API health: `http://127.0.0.1:8091/health`
- Piper API speech: `http://192.168.1.69:8091/v1/audio/speech`

## Project Boundary

- `xiaozhi-esp32-server` = runtime voce
- `xiaozhi-admin-ui` = tool opzionale di management

Il server funziona anche senza Admin UI.

L'Admin UI può aiutare con:
- dashboard servizi
- editor config
- backup / rollback
- restart Xiaozhi e Piper
- log viewer
- device list dai log

Ma:
- non fa parte della pipeline audio
- non è richiesta dal runtime
- non deve introdurre coupling forte col server

## Quick start

1. Segui `SETUP.md`
2. Copia `data/.config.example.yaml` in `data/.config.yaml`
3. Inserisci le tue chiavi e gli endpoint reali
4. Avvia `xiaozhi-esp32-server`
5. Verifica che `piper-api` sia attivo
6. Configura il device con OTA URL
7. Dì `Ciao` e verifica i log

## Documentazione

- `SETUP.md` → installazione e ricostruzione handoff-ready
- `ARCHITECTURE.md` → architettura tecnica e confine dei componenti
- `TODO.md` → attività aperte e roadmap
- `PROJECT_RULES.md` → regole operative del progetto

## Verifiche rapide

### Piper
```bash
systemctl is-active piper-api
curl -s http://127.0.0.1:8091/health ; echo
```

Atteso:
```text
active
{"ok":true}
```

### Xiaozhi
```bash
cd /home/ciru/xiaozhi-esp32-server
docker compose ps
docker compose logs --tail=50
```

### Device
Nei log corretti devono comparire eventi tipo:
- `OTA请求设备ID`
- `收到hello消息`
- `收到listen消息`
- `收到mcp消息`
- `识别文本`
- `语音生成成功`

## Note importanti

- Groq è usato in modalità OpenAI-compatible
- Piper gira locale su Sibilla ed è persistente via systemd
- i log del container mostrano anche IP Docker interni (`172.x`), ma il device usa l'IP LAN reale dell'host
- il path corretto della config runtime è **solo** `data/.config.yaml`
- il file da mettere in GitHub deve essere `.config.example.yaml`, non la config reale con segreti

## Modello config runtime

Per `LLM`, `ASR` e `TTS` il backend supporta ora in modo esplicito un modello a profili:

- `selected_module.LLM` / `ASR` / `TTS` = selezione logica del modulo o driver
- `runtime.llm_profile` / `asr_profile` / `tts_profile` = profilo provider attivo, sorgente preferita interna
- `selected_module.llm` / `asr` / `tts` = compatibilità legacy soltanto
- `LLM` / `ASR` / `TTS` = mappe di profili provider nominati

Esempio della struttura preferita:

```yaml
selected_module:
  LLM: OpenaiLLM
  ASR: GroqASR
  TTS: OpenaiTTS

runtime:
  llm_profile: groq_llama
  asr_profile: groq_whisper
  tts_profile: piper_it

LLM:
  OpenaiLLM:
    type: openai
  groq_llama:
    type: openai
    base_url: https://api.groq.com/openai/v1
    model: llama-3.3-70b-versatile

ASR:
  GroqASR:
    type: groq
  groq_whisper:
    type: groq
    model_name: whisper-large-v3-turbo

TTS:
  OpenaiTTS:
    type: openai
  piper_it:
    type: openai
    base_url: http://192.168.1.69:8091/v1
    model: piper
```

Compatibilità attuale:

- se `runtime.*_profile` manca, i vecchi `selected_module.llm/asr/tts` possono ancora alimentare la normalizzazione
- se il profilo runtime selezionato è assente o invalido, il backend non fallisce in hard startup e torna al base config del modulo logico
- i campi lowercase in `selected_module` restano supportati, ma solo per retrocompatibilità

## Stato roadmap sintetico

Già fatto:
- server Xiaozhi funzionante su Sibilla
- OTA funzionante
- WebSocket funzionante
- Groq ASR funzionante
- Groq LLM funzionante
- Piper locale integrato
- pipeline voce completa funzionante

In corso / successivi:
- mantenere allineata la documentazione server
- continuare evoluzione del progetto separato `xiaozhi-admin-ui`
- migliorare gestione provider/modelli lato configurazione
