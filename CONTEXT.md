# OpenCLAW Essential Context

## WORKING DIRECTORY: `~/.openclaw-mgmt/`

This is the ONLY root folder. All work happens here.

## SSH Access

```bash
# Connect to VM (nosrc user, NOT root)
ssh -i ~/.ssh/id_ed25519_coder nosrc@192.168.100.202
```

## Current Infrastructure

| VM | VMID | IP | Hostname | Status |
|----|------|-----|----------|--------|
| staging | 303 | 192.168.100.202 | openclaw-hl01 | running |
| live | 301 | - | - | stopped |

## Commands

```bash
# Activate venv
source ~/.openclaw-mgmt/.venv/bin/activate

# Check VM status
~/.venv/bin/openclaw-mgmt status
~/.venv/bin/openclaw-mgmt proxmox-status

# Mount shared folder
~/.openclaw-mgmt/scripts/mount-shared.sh mount
```

## Key Files

- `config/config.yaml` - Main configuration
- `openclaw-projects/` - Task management
- `openclaw-knowledgebase/` - RAG knowledgebase (LanceDB)
- `openclaw-docker/` - Docker compose files

## Repos in Knowledgebase

- pai, get-shit-done, happy, firecrawl, agentstack, langchain, llama_index, mxbai-rerank

## Current Issues

- SSH keys for root not working (use nosrc)
- OpenCLAW not installed in VM yet (need docker-compose up)
