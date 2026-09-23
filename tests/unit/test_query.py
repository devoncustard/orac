"""Tests for OrAC query parser."""

import pytest

from orac.config.loader import AppConfig, SensorConfig, MonitoringConfig
from orac.core.query import QueryParser
from orac.sensors.registry import SensorRegistry


@pytest.fixture
def config() -> AppConfig:
    return AppConfig(
        sensors=SensorConfig(),
        monitoring=MonitoringConfig(),
    )


@pytest.fixture
def registry(config: AppConfig) -> SensorRegistry:
    reg = SensorRegistry(config)
    reg.register("sensor.benjamin_temp", "Benjamin's Bedroom", "temperature")
    reg.register("sensor.living_temp", "Living Room", "temperature")
    reg.register("sensor.kitchen_humid", "Kitchen Humidity", "humidity")
    return reg


@pytest.fixture
def parser(config: AppConfig) -> QueryParser:
    return QueryParser(config)


def test_query_temp_specific(parser: QueryParser, registry: SensorRegistry) -> None:
    result = parser.parse("temp benjamin", registry)
    assert result.status == "ok"
    assert result.type == "temp_query"
    assert len(result.data) == 1
    assert "Benjamin" in result.data[0]["friendly_name"]


def test_query_temp_all(parser: QueryParser, registry: SensorRegistry) -> None:
    result = parser.parse("what's the temp", registry)
    assert result.status == "ok"
    assert result.type == "temp_query"
    assert len(result.data) == 2  # Benjamin + Living Room


def test_query_humidity(parser: QueryParser, registry: SensorRegistry) -> None:
    result = parser.parse("humidity kitchen", registry)
    assert result.status == "ok"
    assert result.type == "temp_query"
    assert len(result.data) == 1
    assert "Kitchen" in result.data[0]["friendly_name"]


def test_query_sensors(parser: QueryParser, registry: SensorRegistry) -> None:
    result = parser.parse("sensors", registry)
    assert result.status == "ok"
    assert result.type == "sensor_list"
    assert len(result.data) == 3


def test_query_battery(parser: QueryParser) -> None:
    config = AppConfig(
        sensors=SensorConfig(alert_on_battery_low=20),
        monitoring=MonitoringConfig(),
    )
    reg = SensorRegistry(config)
    reg.register("sensor.batt1", "Mavis", "battery").battery = 15
    reg.register("sensor.batt2", "George", "battery").battery = 90

    result = parser.parse("battery status", reg)
    assert result.status == "ok"
    assert result.type == "battery_report"


def test_query_unknown(parser: QueryParser, registry: SensorRegistry) -> None:
    result = parser.parse("fly my spaceship", registry)
    assert result.status == "error"
    assert "Don't understand" in result.message
