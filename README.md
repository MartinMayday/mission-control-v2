# OpenCLAW Mission Control

Unified system for managing OpenCLAW infrastructure.

## Directory Structure

```
~/.openclaw-mgmt/
├── config/              # Configuration files
│   └── config.yaml     # Main config (Proxmox, instances)
├── scripts/            # Utility scripts
│   └── mount-shared.sh
├── shared/            # Shared folder between local and VM
├── src/               # Mission Control code
│   └── mission_control/
├── tests/             # Test suite
├── openclaw-docker/  # Docker compose files
├── openclaw-projects/# Task management system
├── openclaw-knowledgebase/ # RAG knowledgebase
├── openclaw-backup/   # Backup configs
└── README.md
```

## Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Check status
openclaw-mgmt status

# List instances
openclaw-mgmt list-instances
```

## Configuration

Edit `config/config.yaml` with your Proxmox and instance details.

## SSH Access

VMs are accessed via: `ssh -i ~/.ssh/id_ed25519_coder nosrc@192.168.100.202`

## Shared Folder

Mount shared folder:
```bash
./scripts/mount-shared.sh mount
```

## Current VMs

| Name | VMID | IP | Status |
|------|------|-----|--------|
| openclaw-staging | 303 | 192.168.100.202 | running |
| openclaw-live | 301 | - | stopped |
