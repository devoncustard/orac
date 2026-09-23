"""Home Assistant websocket client."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aiohttp

from orac.config.loader import AppConfig

logger = logging.getLogger("orac.ha_client")

# Sensor discovery patterns
TEMP_SENSOR_DOMAIN = "sensor"
TEMP_SENSOR_DEVICE_CLASS = "temperature"
HUMIDITY_SENSOR_DEVICE_CLASS = "humidity"
BATTERY_SENSOR_DEVICE_CLASS = "battery"


class HAWebSocketClient:
    """Async client for Home Assistant's websocket API."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.url = config.home_assistant.url.rstrip("/")
        self.token = config.home_assistant.access_token
        self.session: aiohttp.ClientSession | None = None
        self.websocket: aiohttp.WSWebSocket | None = None
        self._subscribed = False
        self._last_states: dict[str, Any] = {}

    async def connect(self) -> bool:
        """Connect to HA via websocket and authenticate."""
        try:
            self.session = aiohttp.ClientSession()

            ws_url = self.url.replace("http", "ws") + "/api/websocket"
            self.websocket = await self.session.ws_connect(ws_url)

            # Wait for auth_required
            msg = await self.websocket.receive_json()
            if msg.get("type") != "auth_required":
                logger.warning("Unexpected auth message: %s", msg)

            # Send auth
            auth_msg = {
                "id": 1,
                "type": "auth",
                "access_token": self.token,
            }
            await self.websocket.send_json(auth_msg)

            msg = await self.websocket.receive_json()
            if msg.get("type") == "auth_ok":
                logger.info("HA authentication successful")
                return True
            else:
                logger.error("HA auth failed: %s", msg)
                return False

        except Exception as e:
            logger.error("HA connection failed: %s", e)
            return False

    async def disconnect(self) -> None:
        """Close websocket connection."""
        if self.websocket:
            await self.websocket.close()
        if self.session:
            await self.session.close()
        self.websocket = None
        self.session = None

    async def get_current_states(self) -> dict[str, Any]:
        """Get all entity states from HA."""
        if not self.websocket:
            raise RuntimeError("Not connected to HA")

        msg_id = self._next_id()
        await self.websocket.send_json({"id": msg_id, "type": "get_states"})

        # Listen for response
        while True:
            msg = await self.websocket.receive_json()
            if msg.get("id") == msg_id and msg.get("type") == "result" and msg.get("success"):
                states = {s["entity_id"]: s for s in msg["result"]}
                self._last_states = states
                return states
            elif msg.get("id") == msg_id and msg.get("success") is False:
                raise RuntimeError(f"HA error: {msg}")

    async def subscribe_states(self, callback) -> None:
        """Subscribe to entity state changes via websocket."""
        if not self.websocket:
            raise RuntimeError("Not connected to HA")

        msg_id = self._next_id()
        await self.websocket.send_json({
            "id": msg_id,
            "type": "subscribe_states",
        })

        # Start listening loop
        asyncio.create_task(self._listen_for_states(callback))

    async def _listen_for_states(self, callback) -> None:
        """Listen for state change events."""
        while self.websocket and not self.websocket.closed:
            try:
                msg = await self.websocket.receive_json()
                if msg.get("type") == "state":
                    entity_id = msg["data"]["entity_id"]
                    state = msg["data"]["state"]
                    await callback(entity_id, state)
            except Exception as e:
                logger.error("Error listening to HA events: %s", e)
                break

    async def call_service(self, domain: str, service: str, entity_id: str,
                           data: dict | None = None) -> Any:
        """Call a HA service."""
        if not self.websocket:
            raise RuntimeError("Not connected to HA")

        msg_id = self._next_id()
        payload = {
            "id": msg_id,
            "type": "call_service",
            "domain": domain,
            "service": service,
            "target": {"entity_id": entity_id},
        }
        if data:
            payload["service_data"] = data

        await self.websocket.send_json(payload)

        # Wait for response
        while True:
            msg = await self.websocket.receive_json()
            if msg.get("id") == msg_id:
                return msg

    async def get_weather_forecast(self) -> dict | None:
        """Get weather forecast data."""
        states = await self.get_current_states()
        if "weather.forecast_home" not in states:
            return None
        return states["weather.forecast_home"]

    def discover_sensors(self) -> list[dict]:
        """Discover temperature/humidity sensors from last known states."""
        if not self._last_states:
            return []

        sensors = []
        for entity_id, state in self._last_states.items():
            attrs = state.get("attributes", {})
            device_class = attrs.get("device_class")

            if device_class in (TEMP_SENSOR_DEVICE_CLASS, HUMIDITY_SENSOR_DEVICE_CLASS):
                friendly_name = attrs.get("friendly_name", entity_id)
                sensors.append({
                    "entity_id": entity_id,
                    "friendly_name": friendly_name,
                    "device_class": device_class,
                    "domain": TEMP_SENSOR_DOMAIN,
                })

        return sensors

    def register_sensor(self, sensor: dict) -> None:
        """Register a discovered sensor."""
        self.registry = getattr(self, 'registry', {})
        self.registry[sensor["entity_id"]] = sensor

    @staticmethod
    def _next_id() -> int:
        """Generate a unique message ID."""
        if not hasattr(HAWebSocketClient, '_id_counter'):
            HAWebSocketClient._id_counter = 100
        HAWebSocketClient._id_counter += 1
        return HAWebSocketClient._id_counter
