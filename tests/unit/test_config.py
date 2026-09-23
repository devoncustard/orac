"""Tests for OrAC config loader."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from orac.config.loader import AppConfig, load_config


@pytest.fixture
def temp_config(tmp_path: Path) -> Path:
    """Create a minimal config file for testing."""
    config = {
        "home_assistant": {
            "url": "http://test-ha:8123",
            "access_token": "test-token-123",
        },
        "sensors": {
            "watch": ["sensor.test_temp"],
            "alert_on_temp_high": 35,
            "alert_on_temp_low": 5,
            "alert_on_humidity_high": 80,
            "alert_on_humidity_low": 15,
            "alert_on_battery_low": 10,
        },
        "monitoring": {
            "poll_interval": 30,
            "history_retention": 72,
        },
        "api": {
            "enabled": True,
            "host": "127.0.0.1",
            "port": 9999,
        },
        "alerts": {
            "enabled": True,
            "notify_via": ["notify.test"],
            "tts_via": ["tts.test"],
            "media_player": "media_player.test",
        },
        "voice": {
            "enabled": False,
            "wake_word_model": "porcupine",
            "stt_model": "whisper_tiny",
            "stt_engine": "local",
            "llm_model": "",
            "tts_engine": "ha_tts",
        },
        "logging": {
            "level": "DEBUG",
        },
    }
    path = tmp_path / "test_config.yaml"
    path.write_text(yaml.dump(config))
    return path


def test_load_config(temp_config: Path) -> None:
    config = load_config(temp_config)

    assert config.home_assistant.url == "http://test-ha:8123"
    assert config.home_assistant.access_token == "test-token-123"
    assert "sensor.test_temp" in config.sensors.watch
    assert config.sensors.alert_on_temp_high == 35
    assert config.monitoring.poll_interval == 30
    assert config.api.port == 9999
    assert config.logging.level == "DEBUG"


def test_load_config_defaults(tmp_path: Path) -> None:
    """Test that missing optional fields use defaults."""
    config = {
        "home_assistant": {"url": "http://default:8123", "access_token": ""},
    }
    path = tmp_path / "minimal_config.yaml"
    path.write_text(yaml.dump(config))

    loaded = load_config(path)
    assert loaded.sensors.alert_on_temp_high == 30.0  # default
    assert loaded.sensors.alert_on_temp_low == 10.0  # default
    assert loaded.api.enabled is True
    assert loaded.logging.level == "INFO"


def test_load_config_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Config not found"):
        load_config(tmp_path / "nonexistent.yaml")
