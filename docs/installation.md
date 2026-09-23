# Installation

## System Requirements

- **Python**: 3.13+
- **OS**: macOS, Linux (Raspberry Pi OS), Windows
- **Hardware**: Raspberry Pi 5 recommended for dedicated deployment

## Install from PyPI

```bash
pip install orac
```

## Install from Source

```bash
git clone https://github.com/your-org/orac.git
cd orac
pip install -e .
```

## Install with Dev Dependencies

```bash
pip install -e ".[dev]"
```

## Verify Installation

```bash
orac --version
# orac, version 0.1.0
```

## Platform-Specific Notes

### Raspberry Pi 5

```bash
# Install Python 3.13 (if not already present)
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev

# Create virtual environment
python3.13 -m venv ~/.orac-venv
source ~/.orac-venv/bin/activate

# Install
pip install orac
```

### Home Assistant Add-on

Coming in Phase 2 — OrAC will be packaged as an HA add-on for easy deployment alongside your existing stack.
