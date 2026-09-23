# Project Tasks

## Phase 1 — Climate Monitor + Query Engine ✅

- [x] p1-config — Config loader with YAML defaults and env override
- [x] p1-ha-client — HA WebSocket client (connect, subscribe, discover)
- [x] p1-sensors — Sensor registry with auto-discovery and snapshots
- [x] p1-engine — Main event loop with signal handling
- [x] p1-cli — Click CLI (init, start, query)
- [x] p1-api — REST API (aiohttp, port 8901)
- [x] p1-alerts — Alert manager with deduplication
- [x] p1-tests — 15 unit tests passing

## Phase 2 — Smart Rules Engine 🔜

- [ ] p2-rules-expr — Rule expression parser (if/then/else DSL)
- [ ] p2-rules-builtin — Built-in rules (solar charge, daily briefing, anomaly detection)
- [ ] p2-briefing — Morning briefing system (weather + energy + presence)

## Phase 3 — Voice Interface 🔜

- [ ] p3-voice-wake — Wake word detection (Porcupine)
- [ ] p3-voice-stt — Speech-to-text pipeline (Whisper)
- [ ] p3-voice-llm — Intent parsing (LLM or rule-based)
- [ ] p3-voice-tts — Text-to-speech via HA media players

## Phase 4 — Learning & Context 🔜

- [ ] p4-learn-routines — Context-aware suggestions engine
- [ ] p4-learn-memory — Personalization — learn routines over time
