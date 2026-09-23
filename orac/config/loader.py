"""OrAC configuration loader."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "orac"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"
CONFIG_EXAMPLE_PATH = Path(__file__).resolve().parent.parent.parent / "config.example.yaml"


@dataclass
class HAConfig:
    url: str = "http://127.0.0.1:8123"
    access_token: str = ""


@dataclass
class SensorConfig:
    watch: list[str] = field(default_factory=list)
    alert_on_temp_high: float = 30.0
    alert_on_temp_low: float = 10.0
    alert_on_humidity_high: float = 70.0
    alert_on_humidity_low: float = 20.0
    alert_on_battery_low: int = 20


@dataclass
class MonitoringConfig:
    poll_interval: int = 60
    history_retention: int = 168  # hours


@dataclass
class APIConfig:
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8901


@dataclass
class AlertConfig:
    enabled: bool = True
    notify_via: list[str] = field(default_factory=lambda: ["notify.iphone"])
    tts_via: list[str] = field(default_factory=lambda: ["tts.google_translate_en_com"])
    media_player: str = "media_player.ta_an1000"


@dataclass
class VoiceConfig:
    enabled: bool = False
    wake_word_model: str = "porcupine"
    stt_model: str = "whisper_tiny"
    stt_engine: str = "local"
    llm_model: str = ""
    tts_engine: str = "ha_tts"


@dataclass
class LoggingConfig:
    level: str = "INFO"


@dataclass
class AppConfig:
    home_assistant: HAConfig = field(default_factory=HAConfig)
    sensors: SensorConfig = field(default_factory=SensorConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    api: APIConfig = field(default_factory=APIConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def get_config_path(self) -> Path:
        return DEFAULT_CONFIG_FILE

    def is_configured(self) -> bool:
        return DEFAULT_CONFIG_FILE.exists()

    def init_config(self) -> Path:
        """Create default config file."""
        DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        src = CONFIG_EXAMPLE_PATH
        if src.exists():
            DEFAULT_CONFIG_FILE.write_text(src.read_text())
        else:
            DEFAULT_CONFIG_FILE.write_text(
                "# OrAC Configuration\n"
                "home_assistant:\n"
                "  url: http://127.0.0.1:8123\n"
                "  access_token: ''\n"
            )
        return DEFAULT_CONFIG_FILE


def load_config(path: Path | None = None) -> AppConfig:
    """Load and parse OrAC configuration."""
    config_path = path or DEFAULT_CONFIG_FILE
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config not found at {config_path}. Run 'orac init' first."
        )

    raw = yaml.safe_load(config_path.read_text()) or {}

    def _sub(prefix: str) -> dict:
        return raw.get(prefix, {})

    return AppConfig(
        home_assistant=HAConfig(
            url=_sub("home_assistant").get("url", "http://127.0.0.1:8123"),
            access_token=_sub("home_assistant").get("access_token", ""),
        ),
        sensors=SensorConfig(
            watch=_sub("sensors").get("watch", []),
            alert_on_temp_high=_sub("sensors").get("alert_on_temp_high", 30.0),
            alert_on_temp_low=_sub("sensors").get("alert_on_temp_low", 10.0),
            alert_on_humidity_high=_sub("sensors").get("alert_on_humidity_high", 70.0),
            alert_on_humidity_low=_sub("sensors").get("alert_on_humidity_low", 20.0),
            alert_on_battery_low=_sub("sensors").get("alert_on_battery_low", 20),
        ),
        monitoring=MonitoringConfig(
            poll_interval=_sub("monitoring").get("poll_interval", 60),
            history_retention=_sub("monitoring").get("history_retention", 168),
        ),
        api=APIConfig(
            enabled=_sub("api").get("enabled", True),
            host=_sub("api").get("host", "0.0.0.0"),
            port=_sub("api").get("port", 8901),
        ),
        alerts=AlertConfig(
            enabled=_sub("alerts").get("enabled", True),
            notify_via=_sub("alerts").get("notify_via", ["notify.iphone"]),
            tts_via=_sub("alerts").get("tts_via", ["tts.google_translate_en_com"]),
            media_player=_sub("alerts").get("media_player", "media_player.ta_an1000"),
        ),
        voice=VoiceConfig(
            enabled=_sub("voice").get("enabled", False),
            wake_word_model=_sub("voice").get("wake_word_model", "porcupine"),
            stt_model=_sub("voice").get("stt_model", "whisper_tiny"),
            stt_engine=_sub("voice").get("stt_engine", "local"),
            llm_model=_sub("voice").get("llm_model", ""),
            tts_engine=_sub("voice").get("tts_engine", "ha_tts"),
        ),
        logging=LoggingConfig(
            level=_sub("logging").get("level", "INFO"),
        ),
    )
