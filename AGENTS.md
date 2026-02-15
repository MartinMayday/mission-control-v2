# OpenCLAW Mission Control - Agent Guidelines

## Project Overview

OpenCLAW Mission Control is a unified CLI tool for managing OpenCLAW instances across Proxmox, Docker, and local environments. It provides a centralized interface to monitor, start, stop, and manage multiple OpenCLAW instances.

## Key Commands

- `openclaw-mgmt list` - List all configured instances
- `openclaw-mgmt status` - Check instance status with health info
- `openclaw-mgmt start <name>` - Start an instance
- `openclaw-mgmt stop <name>` - Stop an instance
- `openclaw-mgmt restart <name>` - Restart an instance
- `openclaw-mgmt logs <name>` - View instance logs
- `openclaw-mgmt proxmox-status` - Show Proxmox VM status

## Testing

```bash
pytest mission_control/tests/ -v
```

## Dependencies

Key packages:
- `proxmoxer` - Proxmox VE API wrapper
- `paramiko` - SSH client
- `requests` - HTTP client
- `rich` - Terminal UI
- `typer` - CLI framework

## Architecture

The project follows a modular architecture:
- `models.py` - Data models and configuration
- `manager.py` - Orchestration layer
- `proxmox_client.py` - Proxmox API integration
- `ssh_client.py` - Remote execution
- `health_checker.py` - Health monitoring
- `cli.py` - CLI interface

## Configuration

Edit `config/config.yaml` to add/manage instances. Each instance needs:
- `name`: Unique identifier
- `host`: IP/hostname
- `type`: proxmox, docker, or local
- `vm_id`: For Proxmox VMs
- `openclaw_port`: Port for OpenCLAW health endpoint
