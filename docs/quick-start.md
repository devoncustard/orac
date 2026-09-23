# Quick Start

Get OrAC running in 5 minutes.

## Step 1: Install

```bash
pip install orac
```

## Step 2: Configure

```bash
orac init
```

Edit `~/.config/orac/config.yaml`:

```yaml
home_assistant:
  url: "http://your-ha-ip:8123"
  access_token: "your-long-lived-token-here"
```

## Step 3: Run

```bash
orac start
```

You should see:

```
OrAC butler starting...
  HA URL: http://your-ha-ip:8123
  Poll interval: 60s
  API: enabled
Press Ctrl+C to stop.
```

## Step 4: Query

In another terminal:

```bash
orac query temp
# Lists all temperature sensors

orac query temp benjamin
# Benjamin's temperature

orac query humidity kitchen
# Kitchen humidity

orac query sensors
# List all sensors

orac query battery
# Check battery levels

orac query status
# OrAC status
```

## Step 5: Use the REST API

OrAC exposes an API on port 8901:

```bash
# Health check
curl http://localhost:8901/health

# List all sensors
curl http://localhost:8901/sensors

# Query temperature
curl "http://localhost:8901/query?q=temp benjamin"
```

## Next Steps

- [Configuration Reference](configuration.md) — full config options
- [CLI Reference](cli-reference.md) — all commands
- [Deploy on Raspberry Pi](deploy-pi.md) — production setup
- [Architecture](architecture.md) — how it all works
