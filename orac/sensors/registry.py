"""Sensor registry — tracks discovered sensors and their snapshots."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from orac.config.loader import AppConfig

logger = logging.getLogger("orac.sensors")


@dataclass
class SensorSnapshot:
    entity_id: str
    friendly_name: str
    device_class: str  # temperature or humidity
    value: float | None
    temp: float | None = None
    humidity: float | None = None
    battery: int | None = None
    updated: str = ""

    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "friendly_name": self.friendly_name,
            "device_class": self.device_class,
            "value": self.value,
            "temp": self.temp,
            "humidity": self.humidity,
            "battery": self.battery,
            "updated": self.updated,
        }


class SensorRegistry:
    """In-memory registry of sensor snapshots."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._sensors: dict[str, SensorSnapshot] = {}
        self._history: list[SensorSnapshot] = []
        self._max_history = config.monitoring.history_retention * 360  # 10-min samples

    def register(self, entity_id: str, friendly_name: str,
                 device_class: str, initial_value: float | None = None) -> SensorSnapshot:
        """Register a new sensor."""
        snap = SensorSnapshot(
            entity_id=entity_id,
            friendly_name=friendly_name,
            device_class=device_class,
            value=initial_value,
            updated=datetime.now(timezone.utc).isoformat(),
        )
        # Set derived fields
        if device_class == "temperature":
            snap.temp = initial_value
        elif device_class == "humidity":
            snap.humidity = initial_value
        self._sensors[entity_id] = snap
        logger.debug("Registered sensor: %s (%s)", friendly_name, entity_id)
        return snap

    def update_value(self, entity_id: str, value: float) -> None:
        """Update a sensor's value."""
        if entity_id not in self._sensors:
            logger.warning("Unknown sensor update: %s", entity_id)
            return
        self._sensors[entity_id].value = value
        self._sensors[entity_id].updated = datetime.now(timezone.utc).isoformat()
        self._history.append(self._sensors[entity_id])

    def update_from_states(self, states: dict[str, Any]) -> None:
        """Update all registered sensors from HA states dict."""
        for entity_id, state in states.items():
            if entity_id not in self._sensors:
                continue

            snap = self._sensors[entity_id]
            attrs = state.get("attributes", {})
            state_val = state.get("state")

            try:
                numeric_val = float(state_val)
                snap.value = numeric_val
            except (ValueError, TypeError):
                snap.value = None

            # Extract temp/humidity/battery from state
            if snap.device_class == "temperature":
                snap.temp = snap.value
            elif snap.device_class == "humidity":
                snap.humidity = snap.value
            elif snap.device_class == "battery":
                snap.battery = int(numeric_val) if numeric_val is not None else None

            snap.updated = datetime.now(timezone.utc).isoformat()

        # Add to history
        for snap in self._sensors.values():
            if snap.value is not None:
                self._history.append(snap)

        # Prune old history
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    def register_from_discovery(self, sensors: list[dict]) -> None:
        """Register sensors from HA discovery."""
        for sensor in sensors:
            self.register(
                entity_id=sensor["entity_id"],
                friendly_name=sensor["friendly_name"],
                device_class=sensor["device_class"],
            )

    def get_all(self) -> list[SensorSnapshot]:
        """Get all registered sensors."""
        return list(self._sensors.values())

    def get_by_name(self, name: str) -> list[SensorSnapshot]:
        """Search sensors by friendly name (case-insensitive partial match)."""
        name_lower = name.lower()
        return [s for s in self._sensors.values()
                if name_lower in s.friendly_name.lower()]

    def get_temperatures(self) -> list[SensorSnapshot]:
        """Get all temperature sensors."""
        return [s for s in self._sensors.values() if s.device_class == "temperature"]

    def get_humidity(self) -> list[SensorSnapshot]:
        """Get all humidity sensors."""
        return [s for s in self._sensors.values() if s.device_class == "humidity"]

    def get_low_battery(self) -> list[SensorSnapshot]:
        """Get sensors with low battery."""
        threshold = self.config.sensors.alert_on_battery_low
        return [s for s in self._sensors.values()
                if s.battery is not None and s.battery < threshold]

    def get_history(self, entity_id: str, hours: int = 24) -> list[SensorSnapshot]:
        """Get history for a sensor."""
        return [s for s in self._history
                if s.entity_id == entity_id and
                (datetime.now(timezone.utc) -
                 datetime.fromisoformat(s.updated)).total_seconds() < hours * 3600]
