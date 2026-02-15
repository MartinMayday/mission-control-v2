import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .models import Config, OpenCLAWInstance, InstanceStatus
from .manager import InstanceManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = typer.Typer(help="OpenCLAW Mission Control - Unified Management CLI")
console = Console()


def load_config(config_path: Optional[str] = None) -> Config:
    if config_path is None:
        config_path = str(Path(__file__).parent.parent.parent / "config" / "config.yaml")
    return Config.from_yaml(config_path)


@app.command()
def status(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Instance name"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Check status of OpenCLAW instances"""
    cfg = load_config(config)
    manager = InstanceManager(cfg)

    if name:
        instance = manager.get_instance_by_name(name)
        if not instance:
            console.print(f"[red]Instance '{name}' not found[/red]")
            raise typer.Exit(1)

        manager.update_instance_status(instance)
        display_instance(instance)
    else:
        instances = manager.update_all_instance_statuses()
        display_instances_table(instances)


@app.command()
def start(
    name: str = typer.Argument(..., help="Instance name"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Start an OpenCLAW instance"""
    cfg = load_config(config)
    manager = InstanceManager(cfg)

    console.print(f"[cyan]Starting instance: {name}[/cyan]")
    if manager.start_instance(name):
        console.print(f"[green]Instance '{name}' started successfully[/green]")
    else:
        console.print(f"[red]Failed to start instance '{name}'[/red]")
        raise typer.Exit(1)


@app.command()
def stop(
    name: str = typer.Argument(..., help="Instance name"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Stop an OpenCLAW instance"""
    cfg = load_config(config)
    manager = InstanceManager(cfg)

    console.print(f"[cyan]Stopping instance: {name}[/cyan]")
    if manager.stop_instance(name):
        console.print(f"[green]Instance '{name}' stopped successfully[/green]")
    else:
        console.print(f"[red]Failed to stop instance '{name}'[/red]")
        raise typer.Exit(1)


@app.command()
def restart(
    name: str = typer.Argument(..., help="Instance name"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Restart an OpenCLAW instance"""
    cfg = load_config(config)
    manager = InstanceManager(cfg)

    console.print(f"[cyan]Restarting instance: {name}[/cyan]")
    if manager.restart_instance(name):
        console.print(f"[green]Instance '{name}' restarted successfully[/green]")
    else:
        console.print(f"[red]Failed to restart instance '{name}'[/red]")
        raise typer.Exit(1)


@app.command()
def logs(
    name: str = typer.Argument(..., help="Instance name"),
    lines: int = typer.Option(50, "--lines", "-l", help="Number of log lines"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Get logs from an OpenCLAW instance"""
    cfg = load_config(config)
    manager = InstanceManager(cfg)

    logs = manager.get_instance_logs(name, lines)
    if logs:
        console.print(logs)
    else:
        console.print(f"[red]Failed to get logs for instance '{name}'[/red]")
        raise typer.Exit(1)


@app.command()
def list_instances(
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """List all configured OpenCLAW instances"""
    cfg = load_config(config)
    manager = InstanceManager(cfg)
    instances = manager.get_all_instances()
    display_instances_table(instances)


@app.command()
def proxmox_status(
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Show Proxmox VM status"""
    cfg = load_config(config)
    manager = InstanceManager(cfg)

    vms = manager.get_proxmox_vms()
    if not vms:
        console.print("[yellow]No Proxmox VMs found or not configured[/yellow]")
        return

    table = Table(title="Proxmox VMs")
    table.add_column("VMID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Node", style="blue")

    for vm in vms:
        table.add_row(
            str(vm.get("vmid", "N/A")),
            vm.get("name", "unknown"),
            vm.get("status", "unknown"),
            vm.get("node", "unknown"),
        )

    console.print(table)


def display_instance(instance: OpenCLAWInstance):
    table = Table(title=f"Instance: {instance.name}")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Name", instance.name)
    table.add_row("Host", instance.host)
    table.add_row("Type", instance.type.value)
    table.add_row("Status", instance.status.value)
    table.add_row("Health Check", "✓ Passed" if instance.health_check_passed else "✗ Failed")
    table.add_row("Version", instance.version or "unknown")
    table.add_row("Last Check", instance.last_health_check or "never")
    if instance.error_message:
        table.add_row("Error", instance.error_message)

    console.print(table)


def display_instances_table(instances: list[OpenCLAWInstance]):
    table = Table(title="OpenCLAW Instances")
    table.add_column("Name", style="cyan")
    table.add_column("Host", style="green")
    table.add_column("Type", style="blue")
    table.add_column("Status", style="yellow")
    table.add_column("Health", style="magenta")
    table.add_column("Version", style="white")

    for instance in instances:
        status_color = "green" if instance.status == InstanceStatus.RUNNING else "red"
        health_icon = "✓" if instance.health_check_passed else "✗"
        health_color = "green" if instance.health_check_passed else "red"

        table.add_row(
            instance.name,
            instance.host,
            instance.type.value,
            f"[{status_color}]{instance.status.value}[/{status_color}]",
            f"[{health_color}]{health_icon}[/{health_color}]",
            instance.version or "unknown",
        )

    console.print(table)


def main():
    app()
