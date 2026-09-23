# Contributing

Welcome! OrAC is a collaborative project aimed at building a truly intelligent home butler.

## Project Structure

```
orac/
├── cli.py              # CLI commands (Click)
├── engine.py           # Main event loop
├── config/
│   └── loader.py       # YAML config loading
├── core/
│   ├── ha_client.py    # Home Assistant websocket client
│   └── query.py        # Natural language query parser
├── sensors/
│   └── registry.py     # Sensor registry & snapshot management
├── alerts/
│   └── alert_manager.py # Threshold monitoring
├── api/
│   └── server.py       # REST API (aiohttp)
├── voice/              # Phase 3: STT/LLM/TTS pipeline
tests/
├── unit/               # Unit tests
└── integration/        # Integration tests
docs/
├── index.md            # Home page
├── installation.md     # Install guide
├── configuration.md    # Config reference
├── quick-start.md      # 5-minute setup
├── cli-reference.md    # CLI docs
├── cli/commands.md     # CLI examples
├── api-reference.md    # API docs
├── architecture.md     # Architecture overview
├── phases.md           # Phase roadmap
├── deploy.md           # Deployment guide
├── deploy-pi.md        # Raspberry Pi guide
└── contributing.md     # This file
mkdocs.yml              # MkDocs config
```

## Development Setup

```bash
# Clone
git clone https://github.com/your-org/orac.git
cd orac

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/unit/ -v

# Run linter
ruff check orac/ tests/

# Format code
ruff format orac/ tests/
```

## Running the Dev Server

```bash
# Serve docs locally
pip install mkdocs-material mkdocstrings[python] pymdown-extensions mkdocs-minify-plugin mkdocs-git-revision-date-localized-plugin mike
mkdocs serve
# Open http://localhost:8000
```

## Adding New Features

1. **Create a feature branch**: `git checkout -b feature/your-feature`
2. **Write code** in the appropriate module
3. **Add tests** in `tests/unit/`
4. **Update docs** — if it's a new feature, it needs docs
5. **Run tests**: `pytest tests/unit/ -v`
6. **Run linter**: `ruff check orac/ tests/`
7. **Submit PR**

## Documentation Updates

This site is built with **MkDocs Material**. Docs are in the `docs/` directory.

### Auto-generating API Docs

API docs use **mkdocstrings** to auto-generate from Python docstrings. To update:

```bash
mkdocs build
```

The `mkdocs.yml` config pulls docstrings from:
- `orac.config.loader`
- `orac.core.ha_client`
- `orac.core.query`
- `orac.sensors.registry`
- `orac.alerts.alert_manager`
- `orac.api.server`
- `orac.engine`
- `orac.cli`

### Adding New Pages

1. Create `docs/your-page.md`
2. Add to `nav` section in `mkdocs.yml`

## Coding Standards

- **Python 3.13+** only
- **Type hints** on all functions
- **Google-style docstrings**
- **ruff** for linting and formatting
- **pytest** for testing

## Current Focus

See [phases.md](phases.md) for the current development roadmap.

## Questions?

Open an issue or PR with your ideas!
