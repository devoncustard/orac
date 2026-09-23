# Configuration

OrAC uses a YAML configuration file stored at `~/.config/orac/config.yaml`.

## Initialize

```bash
orac init
```

## Full Configuration Reference

```yaml
home_assistant:
  url: "http://192.168.1.100:8123"     # Your HA instance URL
  access_token: ""                       # Long-lived access token

sensors:
  watch: []                            # Explicit sensor IDs (empty = auto-discover)
  alert_on_temp_high: 30               # °C threshold
  alert_on_temp_low: 10                # °C threshold
  alert_on_humidity_high: 70           # % threshold
  alert_on_humidity_low: 20            # % threshold
  alert_on_battery_low: 20             # % threshold

monitoring:
  poll_interval: 60                    # Seconds between sensor polls
  history_retention: 168               # Hours (7 days)

api:
  enabled: true                        # Enable REST API
  host: "0.0.0.0"                     # Bind address
  port: 8901                          # Port number

alerts:
  enabled: true
  notify_via:
    - "notify.iphone"                  # Home Assistant notification target
  tts_via:
    - "tts.google_translate_en_com"   # TTS engine
  media_player: "media_player.ta_an1000"  # Speaker for voice alerts

voice:
  enabled: false                       # Enable voice features
  wake_word_model: "porcupine"         # Wake word engine
  stt_model: "whisper_tiny"           # Speech-to-text model
  stt_engine: "local"                 # local | openai
  llm_model: ""                       # LLM API endpoint
  tts_engine: "ha_tts"                # Text-to-speech engine

logging:
  level: "INFO"                       # DEBUG | INFO | WARNING | ERROR
```

## Getting a Long-Lived Access Token

1. Open Home Assistant → **Settings** → **People**
2. Click your user name
3. Scroll to **Long-Lived Access Tokens**
4. Generate a new token (name it "OrAC")
5. Copy the token into `config.yaml`

## Environment Variables

The following environment variables can override config values:

| Variable | Overrides |
|----------|-----------|
| `ORAC_HA_URL` | `home_assistant.url` |
| `ORAC_HA_TOKEN` | `home_assistant.access_token` |
| `ORAC_CONFIG_PATH` | Config file location |

## Config Priority

1. Command-line flags (highest)
2. Environment variables
3. `config.yaml`
4. Built-in defaults (lowest)
