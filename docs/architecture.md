# Architecture

OrAC is built on a modular, event-driven architecture designed to run continuously on a dedicated machine.

## High-Level Design

```
┌─────────────────────────────────────────────────────┐
│                    OrAC Core                         │
│                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   Engine    │  │  Sensor     │  │   Alert     │ │
│  │  (event     │  │  Registry   │  │   Manager   │ │
│  │   loop)     │  │             │  │             │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         │                 │                 │        │
│  ┌──────┴──────┐  ┌──────┴──────┐          │        │
│  │  HA         │  │  Query      │          │        │
│  │  WebSocket  │  │  Parser     │          │        │
│  │  Client     │  │             │          │        │
│  └──────┬──────┘  └─────────────┘          │        │
│         │                                   │        │
│  ┌──────┴──────┐                            │        │
│  │  REST API   │                            │        │
│  │  (aiohttp)  │                            │        │
│  └─────────────┘                            │        │
└──────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              Home Assistant                          │
│                                                      │
│  Sensors ──┐                                        │
│  Weather ──┤   entity states, events                │
│  Solar ────┤   service calls                        │
│  Notify ───┘   TTS                                 │
└─────────────────────────────────────────────────────┘
```

## Component Details

### Engine (`orac.engine`)

The heart of OrAC. Manages the asyncio event loop and coordinates all subsystems.

- **`start()`** — Initializes subsystems, connects to HA, starts polling
- **`stop()`** — Graceful shutdown of all tasks
- **`run()`** — Sync entry point with signal handling

### HA WebSocket Client (`orac.core.ha_client`)

Connects to Home Assistant via its WebSocket API (not HTTP polling).

- **`connect()`** — WebSocket handshake + auth
- **`get_current_states()`** — Fetch all entity states
- **`subscribe_states()`** — Listen for state changes in real-time
- **`discover_sensors()`** — Filter for temp/humidity/battery sensors
- **`call_service()`** — Call HA services (TTS, notifications, etc.)

### Sensor Registry (`orac.sensors.registry`)

In-memory store of sensor snapshots with automatic discovery.

- **`register()`** — Add a new sensor
- **`update_from_states()`** — Bulk update from HA states
- **`get_by_name()`** — Fuzzy search by friendly name
- **`get_low_battery()`** — Filter sensors below threshold
- **`get_history()`** — Time-windowed history

### Query Parser (`orac.core.query`)

Natural language to structured queries using regex patterns.

Supported patterns:
- `temp [name]` → temperature query
- `humidity [name]` → humidity query
- `battery` → battery report
- `sensors` → full sensor list
- `status` → OrAC status

### Alert Manager (`orac.alerts.alert_manager`)

Monitors sensor values against configured thresholds.

Alert categories:
- `battery_low` — Sensor battery below threshold
- `temp_high` / `temp_low` — Temperature out of range
- `humidity_high` / `humidity_low` — Humidity out of range

Features:
- Deduplication (same alert won't re-fire)
- Acknowledgment (clear specific alerts)
- Multi-channel dispatch (push, TTS)

### REST API (`orac.api.server`)

aiohttp-based server on configurable port.

| Route | Method | Purpose |
|-------|--------|---------|
| `/health` | GET | Health check |
| `/status` | GET | OrAC status |
| `/sensors` | GET | All sensors |
| `/temp` | GET | Temperature sensors |
| `/query?q=` | GET | Natural language query |

## Data Flow

1. **Discovery** — On startup, HA client fetches all states and filters for temp/humidity/battery sensors
2. **Polling** — Every `monitoring.poll_interval` seconds, engine fetches states and updates registry
3. **Alerting** — After each poll, alert manager checks thresholds and dispatches notifications
4. **Query** — CLI/API requests hit the query parser, which searches the registry and returns results
5. **Heartbeat** — Every 10 minutes, logs sensor count and pending alert count

## Future Phases

| Phase | Component | Description |
|-------|-----------|-------------|
| 2 | Rules Engine | If/then rule expressions with built-in rules |
| 2 | Briefing | Daily morning briefing via TTS/notify |
| 3 | Voice | Wake word → STT → LLM → TTS pipeline |
| 4 | Learning | Context-aware suggestions, routine learning |
