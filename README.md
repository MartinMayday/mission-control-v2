# OpenCLAW Mission Control

Unified Mission Control Center for managing OpenCLAW instances across Proxmox, Docker, and local environments.

## Features

- **Multi-Platform Support**: Manage OpenCLAW instances on Proxmox VMs, Docker containers, and local instances
- **Health Monitoring**: Automatic health checks with status tracking
- **Instance Lifecycle Management**: Start, stop, restart, and monitor instances
- **Log Aggregation**: View logs from any managed instance
- **Rich CLI Interface**: Beautiful terminal UI with tables and colored output
- **Tested & Reliable**: Comprehensive test suite included

## Installation

```bash
cd mission_control
pip install -e .
```

## Configuration

Edit `config/config.yaml` to configure your OpenCLAW instances:

```yaml
openclaw_instances:
  - name: ocdev
    host: 192.168.1.203
    port: 22
    user: nosrc
    type: proxmox
    vm_id: 303
    openclaw_port: 18789

proxmox:
  host: proxmox.homelab.local
  port: 8006
  user: root@pam
  HostName: 192.168.100.201
  Port: 22
  IdentityFile: ~/.ssh/id_ed25519_coder
  token_id: your-token-id
  token_secret: your-token-secret
  verify_ssl: false

```

### Environment Variables

For sensitive credentials, you can use environment variables instead of storing them in config.yaml:

```bash
export PROXMOX_HOST="proxmox.homelab.local"
export PROXMOX_TOKEN_ID="your-token-id"
export PROXMOX_TOKEN_SECRET="your-token-secret"
```

## Usage

### List All Instances

```bash
openclaw-mgmt list
```

### Check Instance Status

```bash
openclaw-mgmt status
openclaw-mgmt status --name ocdev
```

### Start/Stop/Restart Instances

```bash
openclaw-mgmt start ocdev
openclaw-mgmt stop ocdev
openclaw-mgmt restart ocdev
```

### View Logs

```bash
openclaw-mgmt logs ocdev --lines 100
```

### Proxmox VM Status

```bash
openclaw-mgmt proxmox-status
```

## Supported Platforms

### Proxmox

Manage OpenCLAW running inside Proxmox VMs:
- Start/stop VMs via Proxmox API
- Monitor VM health and resources
- SSH access to VMs for detailed management

### Docker

Manage OpenCLAW Docker containers:
- Uses docker-compose under the hood
- SSH to host required for docker commands

### OrbStack (macOS)

Support for OrbStack container management on macOS:
- Detect and manage OrbStack VMs
- Same API as Docker backend

## CLI Tool Integrations

Mission Control can integrate with multiple AI/CLI coding assistants:

| Tool | Path | Description |
|------|------|-------------|
| claude-code | /usr/local/bin/claude | Anthropic's CLI |
| kimi-cli | ~/.local/bin/kimi | Kimi CLI |
| gemini-cli | /usr/local/bin/gemini | Google Gemini CLI |
| codex-cli | /usr/local/bin/codex | OpenAI Codex CLI |
| ampcode | /usr/local/bin/ampcode | Ampcode CLI |
| cursor | /Applications/Cursor.app | Cursor IDE |
| vscode | /usr/local/bin/code | VS Code |
| kilocode | ~/.local/bin/kilocode | KiloCode CLI |
| raycast | /Applications/Raycast.app | Raycast |
| verdent | ~/.local/bin/verdent | Verdent CLI |
| trae | ~/.local/bin/trae | TRAE CLI |
| codebuff | ~/.local/bin/codebuff | CodeBuff CLI |

## Development

### Install Dev Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Quality

```bash
black mission_control/
ruff check mission_control/
mypy mission_control/
```

## Architecture

```
mission_control/
├── src/mission_control/
│   ├── __init__.py       # Package exports
│   ├── models.py         # Data models (Instance, Config, etc.)
│   ├── manager.py        # Instance management orchestration
│   ├── proxmox_client.py # Proxmox API client
│   ├── ssh_client.py     # SSH remote execution
│   ├── health_checker.py # Health monitoring
│   └── cli.py           # CLI interface
├── config/
│   └── config.yaml       # Configuration file
└── tests/
    ├── conftest.py
    ├── test_models.py
    └── test_manager.py
```

## License

MIT
