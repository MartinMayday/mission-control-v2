# OpenClaw Docker Deployment

**Generated:** 2026-02-04
**Deployment Type:** Minimalist Docker
**Status:** Ready to deploy

---

## Critical Security Notes

### ⚠️ CVE Alerts
OpenClaw has TWO critical CVEs that were patched in version **2026.1.29+**:

| CVE | Severity | Description | Status |
|-----|----------|-------------|--------|
| CVE-2026-25253 | CRITICAL | 1-Click Remote Code Execution via crafted link | **PATCHED** in v2026.1.29 |
| CVE-2026-24763 | HIGH | Docker sandbox command injection | **PATCHED** in v2026.1.29 |

**This deployment uses image version 2026.1.29** - both CVEs are patched.

### 🔒 Port 18789 Security
OpenClaw's default port 18789 is **actively scanned by Shodan** (~1,000+ exposed instances).

**This deployment:**
- ✅ Binds to `127.0.0.1` only (localhost)
- ✅ Uses internal Docker network (no public internet exposure)
- ✅ No ports exposed to `0.0.0.0`
- ✅ Safe from Shodan scanning

---

## Quick Start

### 1. Deploy OpenClaw

```bash
cd ~/openclaw-docker
docker-compose up -d
```

### 2. Verify Deployment

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f openclaw

# Health check
docker inspect openclaw | jq '.[0].State.Health'
```

### 3. Access OpenClaw

```bash
# Execute commands inside container
docker exec -it openclaw bash

# Check OpenClaw version (MUST be 2026.1.29+)
docker exec openclaw openclaw --version

# Run OpenClaw CLI commands
docker exec -it openclaw openclaw --help
```

---

## Verification Checklist

Run these commands to verify your deployment is secure:

```bash
# 1. Container is running
docker ps | grep openclaw

# 2. Version is safe (>= 2026.1.29)
docker exec openclaw openclaw --version | grep -E '2026\.1\.(29|[3-9][0-9])'

# 3. No ports exposed to 0.0.0.0 (should be empty)
docker ps | grep openclaw | grep '0.0.0.0'

# 4. Health check passing
docker inspect openclaw | jq '.[0].State.Health.Status'

# 5. Resource usage
docker stats openclaw --no-stream

# 6. Logs for errors
docker-compose logs openclaw | grep -i error

# 7. Network isolation (internal only)
docker network inspect openclaw_openclaw_net | jq '.[0].Internal'

# 8. Read-only filesystem
docker inspect openclaw | jq '.[0].HostConfig.ReadonlyRootfs'
```

**Expected Results:**
- ✅ Container running and healthy
- ✅ Version >= 2026.1.29
- ✅ No 0.0.0.0 port bindings
- ✅ Network is `true` (internal)
- ✅ ReadonlyRootfs is `true`

---

## Configuration

### Environment Variables

Edit `docker-compose.yml` to customize:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCLAW_SAFE_MODE` | `1` | Enable safe mode (disable risky features) |
| `OPENCLAW_TELEMETRY` | `0` | Disable telemetry |
| `OPENCLAW_MCP_ENABLED` | `1` | Enable MCP integration |
| `OPENCLAW_HOST` | `127.0.0.1` | Bind to localhost only |
| `OPENCLAW_PORT` | `8080` | Internal port |

### Resource Limits

Adjust in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'      # Increase for heavier workloads
      memory: 2G     # Increase for local LLM hosting
```

**Minimum for API-based models:** 1 CPU, 1GB RAM
**Recommended for local LLMs:** 4+ CPU, 24GB+ RAM

---

## Integration with Claude Code

To integrate OpenClaw as an MCP server with Claude Code, add to `~/.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "openclaw": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "openclaw",
        "openclaw",
        "mcp",
        "--stdio"
      ]
    }
  }
}
```

Then restart Claude Code to load the MCP server.

---

## Management Commands

### Start/Stop/Restart

```bash
# Start
docker-compose up -d

# Stop
docker-compose stop

# Restart
docker-compose restart

# Destroy (removes containers, keeps volumes)
docker-compose down

# Destroy with volumes (wipes all data)
docker-compose down -v
```

### Logs

```bash
# Follow logs
docker-compose logs -f openclaw

# Last 100 lines
docker-compose logs --tail=100 openclaw

# Logs for specific component
docker-compose logs -f mcp-bridge
```

### Maintenance

```bash
# Update OpenClaw image
docker-compose pull
docker-compose up -d

# Clean up old images
docker image prune -a

# Backup volumes
docker run --rm -v openclaw_config:/data -v $(pwd):/backup alpine tar czf /backup/openclaw_config.tar.gz -C /data .
docker run --rm -v openclaw_data:/data -v $(pwd):/backup alpine tar czf /backup/openclaw_data.tar.gz -C /data .

# Restore volumes
docker run --rm -v openclaw_config:/data -v $(pwd):/backup alpine tar xzf /backup/openclaw_config.tar.gz -C /data
docker run --rm -v openclaw_data:/data -v $(pwd):/backup alpine tar xzf /backup/openclaw_data.tar.gz -C /data
```

---

## Troubleshooting

### Container won't start

```bash
# Check logs for errors
docker-compose logs openclaw

# Verify image exists
docker images | grep openclaw

# Check disk space
df -h
```

### Health check failing

```bash
# Manual health check
docker exec openclaw curl -f http://localhost:8080/health

# Check if process is running
docker exec openclaw ps aux | grep openclaw
```

### Network issues

```bash
# Verify network exists
docker network ls | grep openclaw

# Inspect network
docker network inspect openclaw_openclaw_net

# Test connectivity between containers
docker exec openclaw ping -c 3 mcp-bridge
```

### Permission issues

```bash
# Check volume permissions
docker exec openclaw ls -la /home/openclaw/.config

# Fix permissions if needed
docker exec --user root openclaw chown -R openclaw:openclaw /home/openclaw
```

---

## Security Best Practices

### ✅ What This Deployment Does

- **Version control:** Pinned to v2026.1.29 (patches critical CVEs)
- **Network isolation:** Internal Docker network, no public exposure
- **Localhost binding:** Binds to 127.0.0.1 only
- **Read-only filesystem:** Prevents runtime modifications
- **Dropped capabilities:** Minimal container privileges
- **No telemetry:** Disabled by default
- **Safe mode:** Risky features disabled

### ⚠️ What You SHOULD Do

- **Review logs regularly:** `docker-compose logs -f openclaw`
- **Monitor resource usage:** `docker stats openclaw`
- **Backup volumes:** See backup commands above
- **Update image:** `docker-compose pull` when new versions release
- **Review security advisories:** https://github.com/openclaw/openclaw/security

### 🚫 What You MUST NOT Do

- **NEVER expose port 18789 to 0.0.0.0** - Shodan will find it
- **NEVER use versions before 2026.1.29** - Critical CVEs exist
- **NEVER install untrusted skills** - 341 malicious skills discovered
- **NEVER share API keys in chat** - Skills may log them

---

## Rollback

If you need to remove OpenClaw completely:

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (wipes all data - IRREVERSIBLE)
docker-compose down -v

# Remove images
docker rmi openclaw/openclaw:2026.1.29
docker rmi openclaw/mcp-bridge:latest

# Remove deployment directory
rm -rf ~/openclaw-docker
```

---

## Sources

- [CVE-2026-25253: 1-Click RCE in OpenClaw](https://socradar.io/blog/cve-2026-25253-rce-openclaw-auth-token/)
- [OpenClaw Bug Enables One-Click Remote Code Execution](https://thehackernews.com/2026/02/openclaw-bug-enables-one-click-remote.html)
- [The Open Door: How Shodan is Feasting on Exposed Clawdbot Agents](https://www.penligent.ai/hackinglabs/pt/the-open-door-how-shodan-is-feasting-on-exposed-clawdbot-agents-port-18789-and-the-end-of-security-by-obscurity/)
- [OpenClaw Official Security Documentation](https://docs.openclaw.ai/gateway/security)
- [OpenClaw Security Hardening Guide](https://alirezarezvani.medium.com/openclaw-security-my-complete-hardening-guide-for-vps-and-docker-deployments-14d754edfc1e)
- [Researchers Find 341 Malicious ClawHub Skills](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html)
