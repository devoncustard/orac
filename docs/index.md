# OrAC — Butler of the House

> Your home's dedicated butler bot. Monitors sensors, answers queries, and eventually speaks to you.

![OrAC](assets/orac-icon.svg)

## What is OrAC?

OrAC is a **continuously-running butler bot** that connects to your [Home Assistant](https://www.home-assistant.io/) instance and acts as an intelligent layer on top of your smart home.

### Features

| Feature | Status |
|---------|--------|
| Climate monitoring (temp/humidity) | ✅ Phase 1 |
| Sensor auto-discovery | ✅ Phase 1 |
| Natural language queries | ✅ Phase 1 |
| REST API for on-demand access | ✅ Phase 1 |
| Alert system (battery, temp, humidity) | ✅ Phase 1 |
| Smart rules engine | 🔜 Phase 2 |
| Morning briefing | 🔜 Phase 2 |
| Voice interface (STT → LLM → TTS) | 🔜 Phase 3 |
| Context-aware learning | 🔜 Phase 4 |

## Quick Start

```bash
pip install orac
orac init                    # Create config
orac start                   # Run the butler
orac query temp benjamin    # Ask a question
```

## Architecture

```
┌──────────────────────────────────────┐
│           OrAC Core                   │
├──────────────────────────────────────┤
│  HA WebSocket Client  │  REST API   │
│  Sensor Registry      │  CLI        │
│  Alert Manager        │  Engine     │
│  Query Parser         │             │
└──────────────────────────────────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
  Home Assistant    Your Devices
  (sensors,        (TV, speakers,
   weather,         notifications)
   solar)
```

## Roadmap

- **Phase 1** ✅ — Climate Monitor + Query Engine (current)
- **Phase 2** 🔄 — Smart Rules Engine + Morning Briefing
- **Phase 3** 🔜 — Voice Interface (wake word, STT, LLM, TTS)
- **Phase 4** 🔜 — Context-aware Learning

---

:: { .material-card }

**Want to contribute?** OrAC is open source. Check out our [contributing guide](contributing.md).

::
