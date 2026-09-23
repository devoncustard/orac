# API Reference

OrAC exposes a REST API on port `8901` (configurable).

## Base URL

```
http://localhost:8901
```

## Endpoints

### `GET /health`

Health check endpoint.

**Response:**
```json
{"health": "ok"}
```

### `GET /status`

Get OrAC status.

**Response:**
```json
{
  "status": "running",
  "sensors": 12,
  "pending_alerts": 0
}
```

### `GET /sensors`

List all registered sensors.

**Response:**
```json
{
  "sensors": [
    {
      "entity_id": "sensor.benjamin_temp",
      "friendly_name": "Benjamin's Bedroom",
      "device_class": "temperature",
      "value": 23.4,
      "temp": 23.4,
      "humidity": null,
      "battery": null,
      "updated": "2026-09-23T13:16:16+00:00"
    }
  ],
  "count": 12
}
```

### `GET /temp`

List all temperature sensors.

**Response:**
```json
{
  "temperature_sensors": [
    {
      "entity_id": "sensor.benjamin_temp",
      "friendly_name": "Benjamin's Bedroom",
      "temp": 23.4,
      "updated": "2026-09-23T13:16:16+00:00"
    }
  ],
  "count": 8
}
```

### `GET /query?q=<query>`

Natural language query.

| Parameter | Description | Example |
|-----------|-------------|---------|
| `q` | Query string | `temp benjamin` |

**Response:**
```json
{
  "query": "temp benjamin",
  "type": "temp_query",
  "data": [
    {
      "entity_id": "sensor.benjamin_temp",
      "friendly_name": "Benjamin's Bedroom",
      "temp": 23.4,
      "humidity": null,
      "updated": "2026-09-23T13:16:16+00:00"
    }
  ],
  "message": ""
}
```

**Query Types:**

- `temp_query` — Temperature data
- `sensor_list` — All sensors
- `battery_report` — Battery status
- `status` — OrAC status
- `error` — Parse error

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Bad request (missing `q` or parse error) |
| 500 | Internal server error |
