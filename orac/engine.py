"""OrAC main engine — the butler's brain."""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from datetime import datetime, timezone
from typing import Any

from orac.config.loader import AppConfig
from orac.sensors.registry import SensorRegistry
from orac.core.ha_client import HAWebSocketClient
from orac.alerts.alert_manager import AlertManager

logger = logging.getLogger("orac.engine")


class OrACEngine:
    """The main butler engine. Manages the event loop, sensor registry, and all subsystems."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.running = False
        self.loop: asyncio.AbstractEventLoop | None = None

        # Subsystems
        self.ha_client = HAWebSocketClient(config)
        self.registry = SensorRegistry(config)
        self.alert_manager = AlertManager(config)

        # Polling
        self._poll_task: asyncio.Task | None = None
        self._heartbeat_task: asyncio.Task | None = None

    def _setup_logging(self) -> None:
        level = getattr(logging, self.config.logging.level.upper(), logging.INFO)
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    async def _poll_sensors(self) -> None:
        """Periodically poll HA for sensor states and update registry."""
        interval = self.config.monitoring.poll_interval
        while self.running:
            try:
                states = await self.ha_client.get_current_states()
                self.registry.update_from_states(states)

                # Check alerts
                if self.config.alerts.enabled:
                    alerts = self.alert_manager.check_sensors(self.registry.get_all())
                    for alert in alerts:
                        await self.alert_manager.send_alert(alert)
                        logger.warning("ALERT: %s", alert["message"])

            except Exception as e:
                logger.error("Sensor poll failed: %s", e)

            # Sleep in small increments so we can break on stop
            for _ in range(interval * 10):
                if not self.running:
                    return
                await asyncio.sleep(0.1)

    async def _heartbeat(self) -> None:
        """Periodic heartbeat log."""
        while self.running:
            logger.info(
                "OrAC heartbeat — %d sensors, %d alerts pending",
                len(self.registry.get_all()),
                len(self.alert_manager.get_pending()),
            )
            for _ in range(600):  # every 10 minutes
                if not self.running:
                    return
                await asyncio.sleep(0.1)

    async def start(self) -> None:
        """Start the butler engine."""
        self.running = True
        self._setup_logging()

        logger.info("OrAC butler starting...")
        logger.info("HA URL: %s", self.config.home_assistant.url)
        logger.info("Poll interval: %ds", self.config.monitoring.poll_interval)

        # Connect to HA
        connected = await self.ha_client.connect()
        if not connected:
            logger.error("Failed to connect to Home Assistant. Is it running?")
            raise RuntimeError("HA connection failed")

        logger.info("Connected to Home Assistant!")

        # Auto-discover sensors if none configured
        if not self.config.sensors.watch:
            discovered = self.ha_client.discover_sensors()
            logger.info("Auto-discovered %d sensors: %s",
                        len(discovered),
                        [s["entity_id"] for s in discovered])
            self.registry.register_from_discovery(discovered)

        # Start background tasks
        self._poll_task = asyncio.create_task(self._poll_sensors())
        self._heartbeat_task = asyncio.create_task(self._heartbeat())

        # Start API server if enabled
        if self.config.api.enabled:
            from orac.api.server import start_api_server
            self._api_server = start_api_server(self.registry, self.config.api)

    async def stop(self) -> None:
        """Stop the butler engine gracefully."""
        logger.info("OrAC stopping...")
        self.running = False

        if self._poll_task:
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        if hasattr(self, "_api_server") and self._api_server:
            self._api_server.close()

        await self.ha_client.disconnect()
        logger.info("OrAC stopped.")

    def run(self) -> None:
        """Synchronous entry point."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        loop = self.loop

        def _signal_handler(sig: int) -> None:
            logger.info("Received signal %d", sig)
            asyncio.ensure_future(self.stop(), loop=loop)

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _signal_handler, sig)

        try:
            loop.run_until_complete(self.start())
            loop.run_forever()
        finally:
            loop.run_until_complete(self.stop())
            loop.close()
