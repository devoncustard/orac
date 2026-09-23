"""OrAC REST API server for on-demand queries."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any

from aiohttp import web

from orac.config.loader import APIConfig
from orac.core.query import QueryParser
from orac.sensors.registry import SensorRegistry

logger = logging.getLogger("orac.api")


def _create_app(registry: SensorRegistry, config: AppConfig) -> web.Application:
    """Create the aiohttp web application."""
    from orac.config.loader import load_config

    app = web.Application()

    async def handle_status(request: web.Request) -> web.Response:
        return web.json_response({
            "status": "running",
            "sensors": len(registry.get_all()),
            "pending_alerts": 0,
        })

    async def handle_sensors(request: web.Request) -> web.Response:
        snaps = registry.get_all()
        return web.json_response({
            "sensors": [s.to_dict() for s in snaps],
            "count": len(snaps),
        })

    async def handle_temp(request: web.Request) -> web.Response:
        snaps = [s for s in registry.get_all() if s.temp is not None]
        return web.json_response({
            "temperature_sensors": [s.to_dict() for s in snaps],
            "count": len(snaps),
        })

    async def handle_query(request: web.Request) -> web.Response:
        query_text = request.query.get("q", "")
        if not query_text:
            return web.json_response(
                {"error": "Missing 'q' parameter. Example: /query?q=temp benjamin"},
                status=HTTPStatus.BAD_REQUEST,
            )

        parser = QueryParser(config)
        result = parser.parse(query_text, registry)

        if result.status == "error":
            return web.json_response(
                {"error": result.message},
                status=HTTPStatus.BAD_REQUEST,
            )

        return web.json_response({
            "query": query_text,
            "type": result.type,
            "data": result.data or [],
            "message": result.message,
        })

    async def handle_health(request: web.Request) -> web.Response:
        return web.json_response({"health": "ok"})

    # Register routes
    app.router.add_get("/status", handle_status)
    app.router.add_get("/sensors", handle_sensors)
    app.router.add_get("/temp", handle_temp)
    app.router.add_get("/query", handle_query)
    app.router.add_get("/health", handle_health)

    return app


def start_api_server(registry: SensorRegistry, api_config: APIConfig) -> web.Application:
    """Start the OrAC API server."""
    config = AppConfig()  # minimal config for query parser
    app = _create_app(registry, config)

    runner = web.AppRunner(app)
    app._runner = runner  # type: ignore

    async def _start():
        await runner.setup()
        site = web.TCPSite(runner, api_config.host, api_config.port)
        await site.start()
        logger.info("OrAC API listening on %s:%d", api_config.host, api_config.port)

    asyncio.create_task(_start())
    return app
