# Deploy on Raspberry Pi 5

## Prerequisites

- Raspberry Pi 5 (4GB or 8GB RAM)
- Raspberry Pi OS 64-bit (Bookworm)
- Network access to Home Assistant

## Quick Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.13
sudo apt install -y python3.13 python3.13-venv python3.13-dev python3-pip

# Create OrAC user
sudo useradd -m -s /bin/bash orac

# Switch to orac user
sudo su - orac

# Clone and install
cd ~/projects
git clone https://github.com/your-org/orac.git
cd orac
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .

# Initialize config
orac init
# Edit ~/.config/orac/config.yaml with your HA URL and token

# Test run
orac start
# Ctrl+C to stop

# Set up systemd service
sudo cp /home/orac/projects/orac/deploy/orac.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable orac
sudo systemctl start orac
```

## Service File

Create `/home/orac/projects/orac/deploy/orac.service`:

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

## Power Considerations

The Pi 5 is already very power-efficient. OrAC's memory footprint is minimal:

- **Idle**: ~30 MB RAM
- **With 50 sensors**: ~45 MB RAM
- **CPU**: Near-zero when idle (polling interval)

## SD Card Longevity

OrAC writes no files to disk during normal operation. The only writes are:

- Config file (written once during `orac init`)
- Logs (controlled by `logging.level` in config)

Recommendation: Use a high-endurance SD card or USB SSD boot.
