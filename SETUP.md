# SETUP — Xiaozhi ESP32 Server (Sibilla) — handoff-ready

## Scopo
Questo documento serve a permettere a una persona nuova di ricostruire un sistema funzionante **senza rifare gli errori già incontrati**.

Obiettivo finale:

**ESP32 XiaoZhi-like → Xiaozhi Server su Sibilla → Groq (ASR + LLM) → Piper locale (TTS) → audio sul device**

---

## 0. Assunzioni esplicite

Questa guida assume:

- host Linux già disponibile
- accesso shell al server
- Docker già installato
- `docker compose` funzionante
- Python 3 disponibile
- device ESP32 già flashabile o già flashato
- API key Groq valida
- accesso LAN tra device e server

Setup di riferimento:

- host server: `Sibilla`
- IP LAN host: `192.168.1.69`
- repo server: `/home/ciru/xiaozhi-esp32-server`

---

## 1. Prerequisiti di sistema

Sistema testato:
- Ubuntu / Debian-like

Pacchetti base consigliati:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip docker.io docker-compose-plugin curl
sudo usermod -aG docker $USER
```

Dopo `usermod`:
- fare logout/login
- oppure aprire una nuova sessione shell

Verifiche:

```bash
docker --version
docker compose version
python3 --version
curl --version
```

---

## 2. Stato finale atteso

Alla fine del processo devono risultare funzionanti:

- OTA del device
- WebSocket verso il server
- ASR via Groq
- LLM via Groq
- TTS via Piper locale esposto come API OpenAI-compatible
- riproduzione audio sul device
- controllo volume del device via voce

Segnali di conferma tipici nei log:

- `识别文本:  Ciao.`
- `语音生成成功: Ciao，重试0次`
- `发送音频消息: SentenceType.FIRST, Ciao`
- `收到listen消息`
- `收到mcp消息`

---

## 3. Assunzioni sul device

Device usato nel setup documentato:

- ESP32-S3 tipo XiaoZhi con display rotondo 1.28"
- firmware usato: `2.2.4`
- modello rilevato nei log OTA:
  - `sp-esp32-s3-1.28-box`

Importante:
questa guida parte dal presupposto che il device sia già flashato con firmware compatibile `2.2.4`.

---

## 4. Golden path raccomandata

Procedura breve consigliata:

1. preparare `/home/ciru/xiaozhi-esp32-server`
2. creare `data/.config.example.yaml`
3. copiarlo in `data/.config.yaml`
4. personalizzare la config reale
5. avviare `xiaozhi-esp32-server` con Docker Compose
6. preparare Piper locale e il suo wrapper API OpenAI-compatible
7. verificare `piper-api`
8. configurare il device con OTA URL:
   - `http://192.168.1.69:8003/xiaozhi/ota/`
9. dire `Ciao`
10. verificare log:
   - ASR ok
   - LLM ok
   - TTS ok
   - invio audio ok

---

## 5. Installazione da zero

### 5.1 Clone
```bash
cd /home/ciru
git clone https://github.com/TUO-USERNAME/xiaozhi-esp32-server.git
cd /home/ciru/xiaozhi-esp32-server
mkdir -p data   
cp data/.config.example.yaml data/.config.yaml
```

Se stai usando ancora il repo upstream invece del tuo fork, sostituisci l'URL con quello corretto.

### 5.2 Struttura minima attesa
```text
/home/ciru/xiaozhi-esp32-server
├── docker-compose.yml
├── data/
│   ├── .config.example.yaml
│   └── .config.yaml   ← locale, non da versionare con segreti
└── ...
```

---

## 6. Config runtime

### 6.1 Path corretto (CRITICO)
Usare **solo**:

```text
/home/ciru/xiaozhi-esp32-server/data/.config.yaml
```

Non usare:

```text
/home/ciru/xiaozhi-esp32-server/.config.yaml
```

Se il path è sbagliato, il server non parte o usa una config diversa da quella attesa.

### 6.2 File example da versionare
Mettere in GitHub:

```text
/home/ciru/xiaozhi-esp32-server/data/.config.example.yaml
```

### 6.3 Copia iniziale
```bash
cd /home/ciru/xiaozhi-esp32-server
mkdir -p data
cp data/.config.example.yaml data/.config.yaml
nano data/.config.yaml
```

### 6.4 Campi critici da verificare

#### LLM
- provider OpenAI-compatible verso Groq
- `api_key` valida
- `base_url` corretta
- modello LLM corretto

#### ASR
- provider GroqASR
- `api_key` valida se richiesta dalla struttura config
- modello ASR corretto

#### TTS
- endpoint Piper:
  - `http://192.168.1.69:8091/v1/audio/speech`

#### Intent
Deve essere coerente con la sezione `Intent`.

Errore reale osservato:

```text
KeyError: 'nointentdd'
```

Causa:
- selettore modulo Intent errato nella config

Corretto:
```text
nointent
```

Errato:
```text
nointentdd
```

Effetto:
- crash loop del server

---

## 7. Avvio Xiaozhi server

### 7.1 Avvio
```bash
cd /home/ciru/xiaozhi-esp32-server
docker compose up -d
```

### 7.2 Verifiche
```bash
docker compose ps
docker ps -a --format "table {{.Names}}	{{.Image}}	{{.Status}}"
```

### 7.3 Log
```bash
cd /home/ciru/xiaozhi-esp32-server
docker compose logs --tail=100
```

oppure live:

```bash
cd /home/ciru/xiaozhi-esp32-server
docker compose logs -f --tail=100
```

### 7.4 Porte del server
- `8000` → WebSocket
- `8003` → OTA

### 7.5 Log attesi dopo avvio corretto
```text
初始化组件: llm成功 OpenaiLLM
初始化组件: asr成功 GroqASR
OTA接口是 http://172.x.x.x:8003/xiaozhi/ota/
Websocket地址是 ws://172.x.x.x:8000/xiaozhi/v1/
```

Nota:
nei log compaiono IP Docker interni (`172.x.x.x`), ma il device deve usare l'IP LAN reale dell'host:
- `192.168.1.69`

### 7.6 Test dopo ogni modifica config
Dopo ogni modifica a `data/.config.yaml`:

```bash
cd /home/ciru/xiaozhi-esp32-server
docker compose restart
docker compose logs --tail=50
```

Devi verificare la presenza di righe tipo:

```text
初始化组件: intent成功 nointent
初始化组件: asr成功 GroqASR
初始化组件: llm成功 OpenaiLLM
```

Se una di queste non compare:
- la config è probabilmente rotta o incoerente

---

## 8. Configurazione device

### 8.1 Campo OTA
Nel device usare:

```text
http://192.168.1.69:8003/xiaozhi/ota/
```

### 8.2 Errore da non rifare
Non mettere l'URL WebSocket nel campo OTA.

Il campo OTA serve solo per la richiesta iniziale di configurazione; sarà il server OTA a fornire al device la configurazione WebSocket corretta.

### 8.3 Conferme attese nei log
```text
OTA请求设备ID: ...
未配置MQTT网关，为设备 ... 下发WebSocket配置
设备 ... 固件已是最新: 2.2.4
```

Poi connessione corretta:

```text
收到hello消息
收到listen消息
收到mcp消息
```

---

## 9. Piper locale

Questa guida server assume che Piper locale esista già come componente separato e funzionante.

Verifiche minime:

```bash
systemctl status piper-api --no-pager
curl -s http://127.0.0.1:8091/health ; echo
```

Atteso:

```text
active
{"ok":true}
```

Endpoint TTS usato nel setup:

```text
http://192.168.1.69:8091/v1/audio/speech
```

---

## 10. Verifica completa end-to-end

### 10.1 Dire “Ciao” al device
### 10.2 Controllare nei log Xiaozhi:
- `识别文本`
- `大模型收到用户消息`
- `语音生成成功`
- `发送音频消息`

### 10.3 Atteso
Il device risponde con audio sintetizzato.

---

## 11. Errori reali già incontrati

### 11.1 Manca `data/.config.yaml`
Sintomo:
```text
FileNotFoundError ...
```

Fix:
- creare il file nel path corretto

### 11.2 Campo OTA compilato con WebSocket
Sintomo:
- il device non si configura correttamente

Fix:
- usare l'URL OTA, non l'URL WebSocket

### 11.3 IP Docker confuso con IP LAN
Sintomo:
- si prova a usare `172.x.x.x` dal device

Fix:
- usare sempre l'IP LAN dell'host, qui: `192.168.1.69`

### 11.4 Config runtime incoerente
Errore reale osservato:
```text
KeyError: 'nointentdd'
```

Causa:
- selettore modulo Intent non coerente con la sezione `Intent`

Fix:
- correggere il nome modulo, per esempio da `nointentdd` a `nointent`
- riavviare il server
- verificare che nei log compaia:
  - `初始化组件: intent成功 nointent`

---

## 12. Admin UI opzionale

Esiste un progetto separato:

- `xiaozhi-admin-ui`

Ruolo:
- dashboard
- editor config
- backup / rollback
- restart servizi
- logs
- devices

Importante:
- è un componente esterno
- non va confuso con `xiaozhi-esp32-server`
- non entra nel runtime audio

---

## 13. Checklist finale

Non considerare il setup completo finché non sono veri tutti questi punti:

- [ ] `docker compose ps` mostra Xiaozhi `Up`
- [ ] `data/.config.example.yaml` esiste
- [ ] `data/.config.yaml` esiste nel path corretto
- [ ] `systemctl is-active piper-api` restituisce `active`
- [ ] `curl http://127.0.0.1:8091/health` restituisce `{"ok":true}`
- [ ] il device usa l'OTA URL corretto
- [ ] nei log compaiono `收到hello消息`, `收到listen消息`, `收到mcp消息`
- [ ] il device risponde a `Ciao`
- [ ] TTS audio viene riprodotto sul device
