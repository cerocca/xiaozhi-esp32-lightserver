# ARCHITECTURE — Xiaozhi ESP32 System

## Overview

Sistema distribuito:

**ESP32 → WiFi → WebSocket → Xiaozhi Server → AI services → ritorno audio**

---

## Pipeline voce

1. ESP32 registra audio
2. invio via WebSocket al server
3. server:
   - VAD (Silero)
   - ASR (Groq)
4. testo → LLM (Groq)
5. risposta → TTS (Piper locale via endpoint OpenAI-compatible)
6. audio → ESP32
7. playback sul device

---

## Componenti

### 1. ESP32
- firmware Xiaozhi compatibile
- mic I2S
- speaker
- eventuale display

Nel setup documentato:
- firmware `2.2.4`
- modello visto nei log:
  - `sp-esp32-s3-1.28-box`

---

### 2. Server Xiaozhi (Sibilla)

Esecuzione:
- Docker Compose
- container principale:
  - `xiaozhi-esp32-server`

Responsabilità:
- terminazione WebSocket device
- orchestrazione pipeline vocale
- OTA per il device
- integrazione provider AI

Moduli osservati nel setup:
- VAD: Silero
- ASR: Groq
- LLM: OpenAI-compatible verso Groq
- TTS: provider esterno verso Piper locale

Porte:
- `8000` → WebSocket
- `8003` → OTA

---

### 3. TTS locale (Piper)

Componente separato dal container Xiaozhi.

Caratteristiche:
- locale su host
- endpoint OpenAI-compatible
- persistente via systemd
- porta `8091`

Ruolo:
- riceve testo dal server Xiaozhi
- produce audio sintetizzato
- restituisce audio al server per l'invio al device

---

### 4. Admin UI (opzionale, separata)

Componente esterno:

- progetto: `xiaozhi-admin-ui`
- esecuzione host-native via systemd
- non parte della pipeline audio

Ruolo:
- management
- osservabilità
- editing config
- backup / rollback
- restart servizi
- log viewer
- vista device dai log

Importante:
- non va confusa con `xiaozhi-esp32-server`
- non deve introdurre coupling forte col runtime

---

## Comunicazione

### Device ↔ Server
- protocollo: WebSocket
- audio: Opus / stream device-side
- config iniziale: OTA HTTP

### Server ↔ Groq
- modalità OpenAI-compatible
- usata per:
  - ASR
  - LLM

### Server ↔ Piper
- protocollo: HTTP REST
- endpoint speech OpenAI-compatible

---

## Flusso di boot del device

1. device contatta endpoint OTA
2. server OTA restituisce configurazione
3. device apre WebSocket verso server
4. handshake:
   - `hello`
   - `listen`
   - `mcp`
5. pipeline voce diventa attiva

Segnali tipici nei log:
- `OTA请求设备ID`
- `收到hello消息`
- `收到listen消息`
- `收到mcp消息`

---

## Configurazione runtime

File fondamentale:
```text
/home/ciru/xiaozhi-esp32-server/data/.config.yaml
```

Questo file governa:
- provider ASR
- provider LLM
- provider TTS
- moduli intent/memory/vad
- endpoint e chiavi compatibili

Criticità reale osservata:
- config incoerente può bloccare lo startup
- esempio reale:
  - `KeyError: 'nointentdd'`

Conclusione:
- la config è parte critica del sistema
- ogni modifica va verificata subito con restart + log

---

## Criticità note

- latenza dipendente da Groq
- volume device non sempre coerente con percezione reale
- display firmware non ottimizzato
- config runtime fragile se contiene riferimenti modulo incoerenti
- log con componenti e warning non sempre immediati da leggere

---

## Obiettivo architetturale

- ridurre dipendenze cloud non necessarie
- mantenere stabilità del runtime
- restare compatibili con hardware custom futuri
- conservare un confine pulito tra:
  - runtime voce
  - tooling admin
