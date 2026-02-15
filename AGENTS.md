# OpenCLAW Mission Control - Agent Guidelines

## Project Overview

OpenCLAW Mission Control is a unified CLI tool for managing OpenCLAW instances across Proxmox, Docker, and local environments. It provides a centralized interface to monitor, start, stop, and manage multiple OpenCLAW instances.

## Working Directory

**ALL work must happen in**: `~/.openclaw-mgmt/`

## Build / Lint / Test Commands

### Installation
```bash
cd ~/.openclaw-mgmt
pip install -e ".[dev]"
```

### Running Tests
```bash
# All tests
pytest

# Single test file
pytest tests/test_models.py -v

# Single test
pytest tests/test_models.py::TestOpenCLAWInstance::test_from_dict -v

# With coverage
pytest --cov=src/mission_control --cov-report=term-missing
```

### Code Quality
```bash
# Format code (Black)
black src/mission_control/

# Lint (Ruff)
ruff check src/mission_control/

# Type checking (Mypy)
mypy src/mission_control/

# All checks
black src/mission_control/ && ruff check src/mission_control/ && mypy src/mission_control/
```

### CLI Commands
```bash
# Activate venv first
source .venv/bin/activate

# Or use full path
~/.openclaw-mgmt/.venv/bin/openclaw-mgmt --help

# Common commands
openclaw-mgmt list-instances    # List all configured instances
openclaw-mgmt status           # Check instance status
openclaw-mgmt status --name <instance>  # Check specific instance
openclaw-mgmt start <instance>        # Start instance
openclaw-mgmt stop <instance>         # Stop instance
openclaw-mgmt restart <instance>      # Restart instance
openclaw-mgmt logs <instance>        # View logs
openclaw-mgmt proxmox-status         # Show Proxmox VM status
```

## Code Style Guidelines

### Imports
- Standard library first, then third-party, then local
- Use explicit relative imports for local modules
- Group: stdlib, third-party, local
```python
# Correct
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import proxmoxer
import requests
import typer
import yaml

from mission_control.models import Config, OpenCLAWInstance
from mission_control.manager import InstanceManager
```

### Formatting
- Line length: **100 characters** (enforced by Black)
- Use Black for automatic formatting
- Trailing commas for multi-line structures
```python
# Correct
data = {
    "name": self.name,
    "host": self.host,
    "port": self.port,
}
```

### Types
- Use type hints for all function signatures
- Use `Optional[X]` instead of `X | None`
- Use dataclasses for data models
```python
# Correct
def connect(self) -> ProxmoxAPI:
    ...

def get_vm_status(self, vmid: int) -> dict[str, Any]:
    ...
```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `OpenCLAWInstance`, `ProxmoxClient`)
- **Functions/methods**: `snake_case` (e.g., `get_vm_status`, `check_health`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
- **Private methods**: prefix with `_` (e.g., `_connect`)

### Error Handling
- Use try/except sparingly - only catch specific exceptions
- Log errors with appropriate level
- Re-raise exceptions after logging
- Use tenacity for retries on transient failures
```python
# Correct
logger = logging.getLogger(__name__)

try:
    result = client.connect()
except Exception as e:
    logger.error(f"Failed to connect: {e}")
    raise
```

### Dataclasses
Use `@dataclass` for data models with sensible defaults:
```python
@dataclass
class OpenCLAWInstance:
    name: str
    host: str
    port: int = 22
    user: str = "root"
    type: InstanceType = InstanceType.PROXMOX
```

### Enums
Use Enums for fixed sets of values:
```python
class InstanceStatus(Enum):
    UNKNOWN = "unknown"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
```

## Architecture

```
src/mission_control/
├── __init__.py       # Package exports
├── models.py         # Data models (dataclasses, enums)
├── manager.py        # Orchestration layer
├── proxmox_client.py # Proxmox API integration
├── ssh_client.py    # SSH remote execution
├── health_checker.py # Health monitoring
└── cli.py           # CLI interface (Typer/Rich)
```

## Configuration

Edit `config/config.yaml` - see `config/config.example.yaml` for template.

## SSH Access

```bash
# Connect to VM
ssh -i ~/.ssh/id_ed25519_coder nosrc@192.168.100.202

# NEVER use root - use nosrc user
```

## Testing Best Practices

- One assertion per test when possible
- Use descriptive test names: `test_<method>_<expected_behavior>`
- Mock external dependencies (API calls, network)
- Test both success and failure paths
- Keep tests focused and fast

## Dependencies

Key packages:
- `proxmoxer>=2.0.1` - Proxmox VE API
- `paramiko>=3.4.0` - SSH client
- `requests>=2.31.0` - HTTP client
- `rich>=13.7.0` - Terminal UI
- `typer>=0.9.0` - CLI framework
- `tenacity>=8.2.3` - Retry logic
- `pyyaml>=6.0.1` - Config parsing
- `python-dotenv>=1.0.0` - Environment variables
