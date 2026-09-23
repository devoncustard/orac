# CLI Reference

OrAC provides a command-line interface built with [Click](https://click.palletsprojects.com/).

## Commands

### `orac init`

Initialize configuration at `~/.config/orac/config.yaml`.

```bash
orac init
```

Creates a default config with all available options documented.

### `orac start`

Start the butler engine. Runs indefinitely until stopped.

```bash
orac start
orac start --config /path/to/config.yaml
```

### `orac query <query>`

Query sensor data using natural language.

```bash
orac query temp benjamin
orac query temp
orac query humidity kitchen
orac query humidity
orac query sensors
orac query battery
orac query status
```

### `orac --version`

Display version information.

```bash
orac --version
```

## Query Syntax

OrAC understands natural language patterns:

### Temperature Queries

| Pattern | Example |
|---------|---------|
| `temp <name>` | `orac query temp benjamin` |
| `what's the temp` | `orac query what's the temp` |
| `temperature <name>` | `orac query temperature living room` |

### Humidity Queries

| Pattern | Example |
|---------|---------|
| `humidity <name>` | `orac query humidity kitchen` |
| `what's the humidity` | `orac query what's the humidity` |

### Special Queries

| Pattern | Description |
|---------|-------------|
| `sensors` | List all registered sensors |
| `battery` | Check battery levels |
| `status` | Show OrAC status |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (missing config, query failed) |
