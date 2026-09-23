# OrAC — Butler of the House

Your home's dedicated butler bot. Monitors sensors, answers queries, and eventually speaks to you.

## Quick Start

```bash
pip install -e .
orac init                    # create config in ~/.config/orac/
orac start                   # run the butler
orac query temp benjamin     # ask a question
```

## Configuration

Copy `config.example.yaml` to `~/.config/orac/config.yaml` and edit:

```yaml
home_assistant:
  url: http://your-ha-host:8123
  access_token: your-long-lived-token

sensors:
  alert_on_battery_low: 20    # %
  alert_on_temp_high: 30      # °C
  alert_on_temp_low: 10       # °C
  alert_on_humidity_high: 70  # %
  alert_on_humidity_low: 20   # %
```

## Architecture

- **core/engine** — main event loop, sensor registry, rule engine
- **sensors/** — sensor discovery and data management
- **api/** — query interface (HTTP REST)
- **voice/** — STT/LLM/TTS pipeline
- **alerts/** — notification and alerting system
- **config/** — configuration management

## License

MIT

## Documentation

Full documentation at [docs/](docs/):

```bash
pip install mkdocs-material mkdocstrings[python] pymdown-extensions
mkdocs serve      # serve docs at http://localhost:8000
mkdocs build      # build to site/
./scripts/update-docs.sh   # rebuild docs
```

API docs are auto-generated from source docstrings via mkdocstrings.
