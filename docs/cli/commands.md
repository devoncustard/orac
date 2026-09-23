# CLI Commands

## Detailed command documentation with examples.

### `orac init`

Creates the default configuration file.

```bash
$ orac init
╭────────────────────────────── OrAC ──────────────────────────────╮
│ Config created at:                                               │
│   /home/user/.config/orac/config.yaml                          │
│                                                                  │
│ Edit it and run 'orac start'                                    │
╰──────────────────────────────────────────────────────────────────╯
```

### `orac start`

```bash
$ orac start
OrAC butler starting...
  HA URL: http://192.168.1.100:8123
  Poll interval: 60s
  API: enabled
Press Ctrl+C to stop.
```

### `orac query` Examples

```bash
# Temperature for a specific room
$ orac query temp benjamin
╭──── 🌡️ ─────────────────────────────────────╮
│ Benjamin's Bedroom                           │
│ Temperature: 23.4°C                          │
│ Humidity:    52%                             │
│ Last update: 2026-09-23T13:16:16+00:00      │
╰──────────────────────────────────────────────╯

# All temperatures
$ orac query temp
╭──── 🌡️ ─────────────────────────────────────╮
│ Living Room                                  │
│ Temperature: 24.1°C                          │
│ Humidity:    48%                             │
│ Last update: 2026-09-23T13:15:00+00:00      │
╰──────────────────────────────────────────────╯
╭──── 🌡️ ─────────────────────────────────────╮
│ Kitchen                                      │
│ Temperature: 25.0°C                          │
│ Humidity:    55%                             │
│ Last update: 2026-09-23T13:14:30+00:00      │
╰──────────────────────────────────────────────╯

# List all sensors
$ orac query sensors
Registered sensors:
  • Benjamin's Bedroom: 23.4°C, 52%
  • Living Room: 24.1°C, 48%
  • Kitchen: 25.0°C, 55%
  • TIMMERFLOTTE Moog: 24.8°C, 52%
  • TIMMERFLOTTE Bungle: 25.1°C, 51%
  ...

# Battery report
$ orac query battery
⚠️ 1 sensor(s) have low battery!
  • TIMMERFLOTTE Mavis: 15%

# Status
$ orac query status
╭────────────────── OrAC Status ───────────────────╮
│ HA URL: http://192.168.1.100:8123               │
│ API: enabled                                      │
│ Sensors monitored: auto                           │
│ Alerts: enabled                                   │
╰───────────────────────────────────────────────────╯
```
