"""Tests for OrAC sensor registry."""

from unittest.mock import MagicMock

import pytest

from orac.config.loader import AppConfig, SensorConfig, MonitoringConfig
from orac.sensors.registry import SensorRegistry


@pytest.fixture
def config() -> AppConfig:
    return AppConfig(
        sensors=SensorConfig(alert_on_battery_low=20),
        monitoring=MonitoringConfig(poll_interval=60, history_retention=168),
    )


@pytest.fixture
def registry(config: AppConfig) -> SensorRegistry:
    return SensorRegistry(config)


def test_register_sensor(registry: SensorRegistry) -> None:
    snap = registry.register(
        entity_id="sensor.test_temp",
        friendly_name="Test Temperature",
        device_class="temperature",
        initial_value=22.5,
    )
    assert snap.entity_id == "sensor.test_temp"
    assert snap.temp == 22.5
    assert snap.value == 22.5

    all_sensors = registry.get_all()
    assert len(all_sensors) == 1
    assert all_sensors[0].friendly_name == "Test Temperature"


def test_update_value(registry: SensorRegistry) -> None:
    registry.register(
        entity_id="sensor.test_temp",
        friendly_name="Test Temperature",
        device_class="temperature",
        initial_value=22.0,
    )
    registry.update_value("sensor.test_temp", 23.5)
    snap = registry.get_all()[0]
    assert snap.value == 23.5


def test_update_from_states(registry: SensorRegistry) -> None:
    registry.register(
        entity_id="sensor.test_temp",
        friendly_name="Test Temperature",
        device_class="temperature",
    )

    states = {
        "sensor.test_temp": {
            "state": "24.5",
            "attributes": {"device_class": "temperature"},
        },
    }
    registry.update_from_states(states)
    snap = registry.get_all()[0]
    assert snap.temp == 24.5
    assert snap.value == 24.5


def test_get_by_name(registry: SensorRegistry) -> None:
    registry.register("sensor.temp1", "Benjamin's Bedroom", "temperature")
    registry.register("sensor.temp2", "Living Room", "temperature")
    registry.register("sensor.temp3", "Kitchen", "temperature")

    results = registry.get_by_name("benjamin")
    assert len(results) == 1
    assert "Benjamin" in results[0].friendly_name

    results = registry.get_by_name("room")
    assert len(results) == 2  # Benjamin's Bedroom + Living Room


def test_get_temperatures(registry: SensorRegistry) -> None:
    registry.register("sensor.temp1", "Bedroom", "temperature")
    registry.register("sensor.temp2", "Kitchen", "humidity")
    registry.register("sensor.temp3", "Bathroom", "temperature")

    temps = registry.get_temperatures()
    assert len(temps) == 2
    assert all(s.device_class == "temperature" for s in temps)


def test_get_low_battery(registry: SensorRegistry) -> None:
    registry.register("sensor.batt1", "Mavis", "battery").battery = 15
    registry.register("sensor.batt2", "George", "battery").battery = 85
    registry.register("sensor.batt3", "Zippy", "battery").battery = 10

    low = registry.get_low_battery()
    assert len(low) == 2
    names = {s.friendly_name for s in low}
    assert "Mavis" in names
    assert "Zippy" in names
