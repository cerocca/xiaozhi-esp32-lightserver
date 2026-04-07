# PROJECT RULES — Xiaozhi ESP32 Server

## Regola fondamentale
I file Markdown (`.md`) vengono aggiornati **solo su richiesta esplicita dell'utente**.

---

## Filosofia del progetto

- non rompere ciò che funziona
- preferire semplicità e controllo
- evitare dipendenze inutili o chiuse
- design stile RevK:
  - pulito
  - stabile
  - comprensibile

---

## Metodo di lavoro

- prima funzionante, poi miglioramento
- ogni modifica deve essere verificabile
- debug prima delle feature nuove
- log sempre prioritari
- modifiche piccole e reversibili

---

## Cosa evitare

- refactor inutili
- cambi multipli non testati
- introduzione di complessità non necessaria
- accoppiare troppo runtime server e tooling admin

---

## Confine con Admin UI

Il progetto `xiaozhi-admin-ui` è separato da `xiaozhi-esp32-server`.

Regola:
- il server resta il runtime voce
- l'Admin UI resta il tooling di management

Da evitare:
- spostare logica runtime dentro l'Admin UI
- trattare l'Admin UI come parte del server
- introdurre dipendenze forti del server dalla UI

---

## Approccio

- iterativo
- conservativo
- orientato a sistema reale, non demo
- documentazione e stato reale devono restare coerenti
