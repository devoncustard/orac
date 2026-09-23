# Development Phases

OrAC is being built in four phases, each adding significant capabilities.

## Phase 1 — Climate Monitor + Query Engine ✅

**Status:** Complete. All 15 tests passing.

### Components

- **Config System** — YAML config with defaults, `~/.config/orac/config.yaml`
- **HA WebSocket Client** — Connect, subscribe, discover sensors
- **Sensor Registry** — Auto-discovery, snapshot management, history
- **Query Parser** — Natural language parsing (temp, humidity, battery)
- **REST API** — aiohttp server with `/sensors`, `/query`, `/health`
- **Alert Manager** — Threshold monitoring with deduplication
- **CLI** — Click-based interface with `init`, `start`, `query` commands

### Files

```
orac/
├── cli.py              # CLI commands
├── engine.py           # Main event loop
├── config/loader.py    # Config loading
├── core/
│   ├── ha_client.py    # HA websocket client
│   └── query.py        # Query parser
├── sensors/registry.py # Sensor registry
├── alerts/alert_manager.py
└── api/server.py       # REST API
```

## Phase 2 — Smart Rules Engine 🔜

### Planned Components

- **Rule Expression Parser** — DSL for if/then/else rules
- **Built-in Rules**
  - Solar peak → charge battery
  - Rain detected → close blinds
  - Daily briefing → TTS announcement
  - Anomaly detection → alert on unusual patterns
- **Morning Briefing** — Weather + energy + presence summary

### Config Format

```yaml
rules:
  - name: "solar_charge"
    condition: "solar_production > 5.0 kW AND battery_soc < 90"
    action: "set_charge_rate(max)"
  - name: "rain_blinds"
    condition: "weather.forecast_home.precipitation > 1"
    action: "close_cover.living_room"
```

## Phase 3 — Voice Interface 🔜

### Planned Components

- **Wake Word Detection** — Porcupine/Picovoice local wake word
- **Speech-to-Text** — Whisper (local) or OpenAI API
- **Intent Parser** — LLM-based intent extraction
- **Text-to-Speech** — HA TTS or local engine

### Voice Flow

```
Audio Input → Wake Word → STT → LLM → Intent → Action → TTS → Audio Output
```

## Phase 4 — Learning & Context 🔜

### Planned Components

- **Context-Aware Suggestions** — "It's getting dark, want me to turn on the lights?"
- **Routine Learning** — Learn patterns over time
- **Personalization** — Adapt to user preferences

## Contributing

See [contributing.md](contributing.md) for how to help with any phase.
