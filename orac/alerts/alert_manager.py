"""Alert manager — checks sensors and sends notifications."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from orac.config.loader import AppConfig
from orac.sensors.registry import SensorSnapshot

logger = logging.getLogger("orac.alerts")


@dataclass
class Alert:
    level: str  # warning, critical
    sensor_name: str
    sensor_id: str
    message: str
    category: str  # battery, temp_high, temp_low, humidity_high, humidity_low, offline
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class AlertManager:
    """Manage sensor alerts and notifications."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._pending: list[Alert] = []
        self._acknowledged: list[Alert] = []
        self._sent: set[str] = set()  # dedup by (sensor_id, category)

    def check_sensors(self, snapshots: list[SensorSnapshot]) -> list[Alert]:
        """Check all sensors and return any new alerts."""
        new_alerts = []

        for snap in snapshots:
            key = (snap.entity_id, "battery")

            # Battery check
            if snap.battery is not None and snap.battery < self.config.sensors.alert_on_battery_low:
                if key not in self._sent:
                    alert = Alert(
                        level="warning",
                        sensor_name=snap.friendly_name,
                        sensor_id=snap.entity_id,
                        message=f"Low battery: {snap.friendly_name} at {snap.battery}%",
                        category="battery_low",
                    )
                    new_alerts.append(alert)
                    self._sent.add(key)

            # Temperature checks
            if snap.temp is not None:
                if snap.temp > self.config.sensors.alert_on_temp_high:
                    k = (snap.entity_id, "temp_high")
                    if k not in self._sent:
                        new_alerts.append(Alert(
                            level="warning",
                            sensor_name=snap.friendly_name,
                            sensor_id=snap.entity_id,
                            message=f"High temperature: {snap.friendly_name} at {snap.temp:.1f}°C",
                            category="temp_high",
                        ))
                        self._sent.add(k)

                elif snap.temp < self.config.sensors.alert_on_temp_low:
                    k = (snap.entity_id, "temp_low")
                    if k not in self._sent:
                        new_alerts.append(Alert(
                            level="critical",
                            sensor_name=snap.friendly_name,
                            sensor_id=snap.entity_id,
                            message=f"Low temperature: {snap.friendly_name} at {snap.temp:.1f}°C",
                            category="temp_low",
                        ))
                        self._sent.add(k)

            # Humidity checks
            if snap.humidity is not None:
                if snap.humidity > self.config.sensors.alert_on_humidity_high:
                    k = (snap.entity_id, "humid_high")
                    if k not in self._sent:
                        new_alerts.append(Alert(
                            level="warning",
                            sensor_name=snap.friendly_name,
                            sensor_id=snap.entity_id,
                            message=f"High humidity: {snap.friendly_name} at {snap.humidity:.0f}%",
                            category="humidity_high",
                        ))
                        self._sent.add(k)

                elif snap.humidity < self.config.sensors.alert_on_humidity_low:
                    k = (snap.entity_id, "humid_low")
                    if k not in self._sent:
                        new_alerts.append(Alert(
                            level="warning",
                            sensor_name=snap.friendly_name,
                            sensor_id=snap.entity_id,
                            message=f"Low humidity: {snap.friendly_name} at {snap.humidity:.0f}%",
                            category="humidity_low",
                        ))
                        self._sent.add(k)

        self._pending.extend(new_alerts)
        return new_alerts

    async def send_alert(self, alert: Alert) -> None:
        """Send an alert via configured channels."""
        logger.info("Sending alert: %s", alert.message)
        # TODO: Implement actual notification (iPhone push, TTS, etc.)
        # This is a placeholder for the notification dispatch

    def get_pending(self) -> list[Alert]:
        return list(self._pending)

    def get_pending_count(self) -> int:
        return len(self._pending)

    def ack_alert(self, sensor_id: str, category: str) -> None:
        """Acknowledge an alert so it won't re-fire."""
        self._sent.add((sensor_id, category))
        self._pending = [a for a in self._pending
                         if not (a.sensor_id == sensor_id and a.category == category)]
