# OrAC — Raspberry Pi 5 Deployment Guide

## Prerequisites

- Raspberry Pi 5 with Raspberry Pi OS (64-bit)
- Network access to Home Assistant instance
- Python 3.13+

## Quick Install

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and deps
sudo apt install -y python3.13 python3.13-venv python3-pip

# Create OrAC user
sudo useradd -m -s /bin/bash orac

# Switch to orac user
sudo su - orac

# Clone and install
cd ~/projects
git clone <your-repo> orac
cd orac
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .

# Initialize config
orac init
# Edit ~/.config/orac/config.yaml with your HA URL and access token
```

## Systemd Service

Create `/etc/systemd/system/orac.service`:

```ini
[Unit]
Description=OrAC Butler Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=orac
Group=orac
WorkingDirectory=/home/orac/projects/orac
Environment=PATH=/home/orac/projects/orac/.venv/bin:/usr/bin:/bin
ExecStart=/home/orac/projects/orac/.venv/bin/orac start
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable orac
sudo systemctl start orac

# Check status
sudo systemctl status orac
journalctl -u orac -f
```

## Configuration

Edit `~/.config/orac/config.yaml`:

```yaml
home_assistant:
  url: "http://<your-ha-ip>:8123"
  access_token: "<your-long-lived-token>"
```

### Getting a Long-Lived Access Token

1. Open Home Assistant → Settings → People
2. Click your user name
3. Scroll to "Long-Lived Access Tokens"
4. Generate a new token (name it "OrAC")
5. Copy the token into config.yaml

## API Access

Once running, OrAC exposes a REST API on port 8901:

```bash
# Health check
curl http://localhost:8901/health

# List all sensors
curl http://localhost:8901/sensors

# Query temperature
curl "http://localhost:8901/query?q=temp benjamin"
```

## CLI Usage

```bash
orac init                    # Create config
orac query temp benjamin    # Query a sensor
orac query sensors           # List all sensors
orac query battery           # Check battery levels
orac start                   # Start the butler
```

## Updating

```bash
cd ~/projects/orac
git pull
source .venv/bin/activate
pip install -e .
sudo systemctl restart orac
```
