"""Query parser — turns user text into structured queries."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from orac.config.loader import AppConfig
from orac.sensors.registry import SensorRegistry


@dataclass
class QueryResult:
    type: str  # temp_query, sensor_list, status, error
    data: list[dict] | None = None
    message: str = ""
    status: str = "ok"


class QueryParser:
    """Parse natural language queries into structured requests."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.registry = SensorRegistry(config)

    def parse(self, query_text: str, registry: SensorRegistry | None = None) -> QueryResult:
        """Parse a query string and return a result."""
        q = query_text.strip().lower()
        reg = registry or self.registry

        # Check for status
        if q in ("status", "how are you", "what's up", "hello", "hi orac"):
            return QueryResult(type="status")

        # Check for sensor list
        if q in ("sensors", "list sensors", "what sensors", "show sensors"):
            snaps = reg.get_all()
            return QueryResult(
                type="sensor_list",
                data=[s.to_dict() for s in snaps],
            )

        # Temperature queries
        temp_patterns = [
            (r"what.*temp(erature)?\s*(in|of|for|at)?\s*(.*)", 3),
            (r"temp(erature)?\s+(in|of|for|at)?\s*(.*)", 3),
            (r"temp(erature)?\s+(.*)", 2),
            (r"how\s+hot|cold\s*(.*)", 1),
            (r"what's?\s+the\s+temp(erature)?", None),
        ]
        for pattern, loc_idx in temp_patterns:
            m = re.match(pattern, q)
            if m:
                location = m.group(loc_idx) if loc_idx and m.lastindex and m.lastindex >= loc_idx else ""
                return self._query_temp(location.strip() or "", reg)

        # Humidity queries
        hum_patterns = [
            (r"what.*humidit(y|y)?\s*(in|of|for|at)?\s*(.*)", 4),
            (r"humidit(y|y)?\s+(in|of|for|at)?\s*(.*)", 4),
            (r"humidit(y|y)?\s+(.*)", 2),
            (r"what's?\s+the\s+humidit(y|y)?", None),
        ]
        for pattern, loc_idx in hum_patterns:
            m = re.match(pattern, q)
            if m:
                location = m.group(loc_idx) if loc_idx and m.lastindex and m.lastindex >= loc_idx else ""
                return self._query_humidity(location.strip() or "", reg)

        # Battery queries
        bat_patterns = [
            r"batter(y|ies)\s*(status|level|low|check|report)?",
            r"check\s+batter(y|ies)",
        ]
        for pattern in bat_patterns:
            m = re.match(pattern, q)
            if m:
                return self._query_battery(reg)

        return QueryResult(
            type="error",
            message=f"Don't understand: '{query_text}'. Try 'temp benjamin' or 'sensors'.",
            status="error",
        )

    def _query_temp(self, location: str, reg: SensorRegistry) -> QueryResult:
        if location:
            snaps = reg.get_by_name(location)
            temp_snaps = [s for s in snaps if s.device_class == "temperature"]
        else:
            temp_snaps = reg.get_temperatures()

        if not temp_snaps:
            return QueryResult(
                type="temp_query",
                data=[],
                message="No temperature sensors found.",
                status="ok",
            )

        return QueryResult(
            type="temp_query",
            data=[s.to_dict() for s in temp_snaps],
        )

    def _query_humidity(self, location: str, reg: SensorRegistry) -> QueryResult:
        if location:
            snaps = reg.get_by_name(location)
            hum_snaps = [s for s in snaps if s.device_class == "humidity"]
        else:
            hum_snaps = reg.get_humidity()

        if not hum_snaps:
            return QueryResult(
                type="error",
                message="No humidity sensors found.",
                status="error",
            )

        return QueryResult(
            type="temp_query",
            data=[s.to_dict() for s in hum_snaps],
        )

    def _query_battery(self, reg: SensorRegistry) -> QueryResult:
        low = reg.get_low_battery()
        all_bat = [s for s in reg.get_all() if s.battery is not None]

        result = {
            "type": "battery_report",
            "low_battery": [s.to_dict() for s in low],
            "all_battery": [s.to_dict() for s in all_bat],
            "low_count": len(low),
            "total_count": len(all_bat),
        }

        if low:
            return QueryResult(
                type="battery_report",
                data=[result],
                message=f"⚠️ {len(low)} sensor(s) have low battery!",
            )
        return QueryResult(
            type="battery_report",
            data=[result],
            message="All batteries are healthy.",
        )
