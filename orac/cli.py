"""OrAC CLI — Butler of the House."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.panel import Panel

from orac.config.loader import DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILE, load_config

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """OrAC — Butler of the House. Your home's dedicated butler bot."""
    pass


@main.command()
def init() -> None:
    """Initialize OrAC configuration."""
    config_dir = DEFAULT_CONFIG_DIR
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = DEFAULT_CONFIG_FILE
    if config_file.exists():
        console.print(f"[yellow]Config already exists at {config_file}[/yellow]")
        console.print("  Run [bold]orac init --overwrite[/bold] to replace it.")
        return

    # Write defaults
    defaults = {
        "home_assistant": {
            "url": "http://192.168.1.100:8123",
            "access_token": "",
        },
        "sensors": {
            "watch": [],
            "alert_on_temp_high": 30,
            "alert_on_temp_low": 10,
            "alert_on_humidity_high": 70,
            "alert_on_humidity_low": 20,
            "alert_on_battery_low": 20,
        },
        "monitoring": {
            "poll_interval": 60,
            "history_retention": 168,
        },
        "api": {
            "enabled": True,
            "host": "0.0.0.0",
            "port": 8901,
        },
        "alerts": {
            "enabled": True,
            "notify_via": ["notify.iphone"],
            "tts_via": ["tts.google_translate_en_com"],
            "media_player": "media_player.ta_an1000",
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
            "level": "INFO",
        },
    }

    config_file.write_text(yaml.dump(defaults, default_flow_style=False))
    console.print(Panel(
        f"[green]Config created at:[/green]\n  {config_file}",
        title="[bold]OrAC[/bold]",
        subtitle="Edit it and run 'orac start'",
    ))


@main.command()
@click.option("--config", "-c", "config_path", type=click.Path(),
              help="Path to config file (default: ~/.config/orac/config.yaml)")
def start(config_path: str | None) -> None:
    """Start the OrAC butler engine."""
    from orac.engine import OrACEngine

    path = Path(config_path) if config_path else None
    try:
        config = load_config(path)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        console.print("Run [bold]orac init[/bold] first to create a config.")
        sys.exit(1)

    engine = OrACEngine(config)
    console.print("[bold green]OrAC butler starting...[/bold green]")
    console.print(f"  HA URL: {config.home_assistant.url}")
    console.print(f"  Poll interval: {config.monitoring.poll_interval}s")
    console.print(f"  API: {'enabled' if config.api.enabled else 'disabled'}")
    console.print("[dim]Press Ctrl+C to stop.[/dim]")

    try:
        engine.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]OrAC stopping...[/yellow]")
        engine.stop()
        console.print("[dim]Goodbye, monke.[/dim]")


@main.command()
@click.option("--config", "-c", "config_path", type=click.Path(),
              help="Path to config file")
@click.argument("query", nargs=-1, required=True)
def query(config_path: str | None, query: tuple[str, ...]) -> None:
    """Query OrAC for sensor data.

    Examples:
      orac query temp benjamin
      orac query temp
      orac query status
      orac query sensors
    """
    from orac.core.query import QueryParser
    from orac.config.loader import load_config

    path = Path(config_path) if config_path else None
    try:
        config = load_config(path)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    query_text = " ".join(query)
    parser = QueryParser(config)
    result = parser.parse(query_text)

    if result.status == "error":
        console.print(f"[red]Error:[/red] {result.message}")
        sys.exit(1)

    # Display results
    if result.type == "sensor_list":
        if result.data:
            console.print("[bold]Registered sensors:[/bold]")
            for s in result.data:
                console.print(f"  • {s['name']}: {s['temp']:.1f}°C, {s['humidity']:.0f}%")
        else:
            console.print("[yellow]No sensors registered yet. Run 'orac start' first.[/yellow]")

    elif result.type == "temp_query":
        if result.data:
            for s in result.data:
                console.print(Panel(
                    f"[bold]{s['name']}[/bold]\n"
                    f"Temperature: [red]{s['temp']:.1f}°C[/red]\n"
                    f"Humidity:    [blue]{s['humidity']:.0f}%[/blue]\n"
                    f"Last update: {s['updated']}",
                    title="[bold]🌡️[/bold]",
                    border_style="green",
                ))
        else:
            console.print("[yellow]No matching sensors found.[/yellow]")

    elif result.type == "status":
        console.print(Panel(
            f"HA URL: {config.home_assistant.url}\n"
            f"API: {'enabled' if config.api.enabled else 'disabled'}\n"
            f"Sensors monitored: {len(config.sensors.watch) or 'auto'}\n"
            f"Alerts: {'enabled' if config.alerts.enabled else 'disabled'}",
            title="[bold]OrAC Status[/bold]",
        ))


if __name__ == "__main__":
    main()
