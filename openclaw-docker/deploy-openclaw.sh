#!/bin/bash

# =============================================================================
# OpenClaw Secure Docker Deployment Script
# =============================================================================
# Based on official OpenClaw docker-setup.sh with security modifications:
# - Binds to localhost only (127.0.0.1) instead of all interfaces (lan)
# - Uses official OpenClaw repository and build process
# - Creates isolated directories for config and workspace
# =============================================================================

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

REPO_DIR="$HOME/openclaw-docker/repository"
COMPOSE_FILE="$REPO_DIR/docker-compose.yml"

echo "🔒 OpenClaw Secure Docker Deployment"
echo "===================================="
echo ""

# Check dependencies
require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo -e "${RED}❌ Missing dependency: $1${NC}" >&2
    exit 1
  fi
}

echo "1. Checking dependencies..."
require_cmd docker
if ! docker compose version >/dev/null 2>&1; then
  echo -e "${RED}❌ Docker Compose not available${NC}" >&2
  exit 1
fi
echo -e "${GREEN}✅ Dependencies OK${NC}"
echo ""

# Setup directories
echo "2. Setting up directories..."
OPENCLAW_CONFIG_DIR="${OPENCLAW_CONFIG_DIR:-$HOME/.openclaw}"
OPENCLAW_WORKSPACE_DIR="${OPENCLAW_WORKSPACE_DIR:-$HOME/openclaw-workspace}"

mkdir -p "$OPENCLAW_CONFIG_DIR"
mkdir -p "$OPENCLAW_WORKSPACE_DIR"

echo "   Config dir: $OPENCLAW_CONFIG_DIR"
echo "   Workspace:  $OPENCLAW_WORKSPACE_DIR"
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Security: Generate gateway token
echo "3. Generating security token..."
if [[ -z "${OPENCLAW_GATEWAY_TOKEN:-}" ]]; then
  if command -v openssl >/dev/null 2>&1; then
    OPENCLAW_GATEWAY_TOKEN="$(openssl rand -hex 32)"
  else
    OPENCLAW_GATEWAY_TOKEN="$(python3 - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
)"
  fi
fi
export OPENCLAW_GATEWAY_TOKEN
echo -e "${GREEN}✅ Token generated${NC}"
echo ""

# Build Docker image
echo "4. Building OpenClaw Docker image..."
cd "$REPO_DIR"
if ! docker build -t openclaw:local -f Dockerfile .; then
  echo -e "${RED}❌ Failed to build Docker image${NC}" >&2
  exit 1
fi
echo -e "${GREEN}✅ Docker image built${NC}"
echo ""

# Security: Set environment variables for secure deployment
echo "5. Configuring secure environment..."
export OPENCLAW_CONFIG_DIR
export OPENCLAW_WORKSPACE_DIR
export OPENCLAW_GATEWAY_PORT="${OPENCLAW_GATEWAY_PORT:-18789}"
export OPENCLAW_BRIDGE_PORT="${OPENCLAW_BRIDGE_PORT:-18790}"
# CRITICAL: Bind to localhost only, not all interfaces
export OPENCLAW_GATEWAY_BIND="${OPENCLAW_GATEWAY_BIND:-localhost}"
export OPENCLAW_IMAGE="openclaw:local"

echo "   Gateway port: $OPENCLAW_GATEWAY_PORT"
echo "   Bridge port:  $OPENCLAW_BRIDGE_PORT"
echo "   ⚠️  Binding:    localhost (127.0.0.1) only - NOT exposed to internet"
echo -e "${GREEN}✅ Environment configured${NC}"
echo ""

# Start OpenClaw
echo "6. Starting OpenClaw containers..."
cd "$REPO_DIR"
if ! docker compose up -d; then
  echo -e "${RED}❌ Failed to start containers${NC}" >&2
  exit 1
fi
echo -e "${GREEN}✅ Containers started${NC}"
echo ""

# Verify deployment
echo "7. Verifying deployment..."
sleep 3 # Give containers time to start

if docker ps | grep -q openclaw; then
  echo -e "${GREEN}✅ OpenClaw gateway is running${NC}"
  echo ""
  echo "===================================="
  echo "🎉 Deployment Complete!"
  echo "===================================="
  echo ""
  echo "Container Status:"
  docker compose ps
  echo ""
  echo "Next Steps:"
  echo "  1. Run onboarding: docker compose run --rm openclaw-cli onboard"
  echo "  2. Check status:    docker compose run --rm openclaw-cli status"
  echo "  3. View logs:       docker compose logs -f"
  echo "  4. Access CLI:      docker compose run --rm openclaw-cli --help"
  echo ""
  echo "⚠️  Security Note:"
  echo "  - Port 18789 is bound to 127.0.0.1 only (localhost)"
  echo "  - NOT exposed to the internet (Shodan-safe)"
  echo "  - Do NOT change OPENCLAW_GATEWAY_BIND to 'lan' or '0.0.0.0'"
  echo ""
  echo "📖 Documentation:"
  echo "  - Simon Willison's guide: https://til.simonwillison.net/llms/openclaw-docker"
  echo "  - Official docs: https://docs.openclaw.ai/"
  echo ""
  echo "🔍 Management Commands:"
  echo "  - Stop:  docker compose stop"
  echo "  - Start: docker compose start"
  echo "  - Restart: docker compose restart"
  echo "  - Remove: docker compose down"
else
  echo -e "${RED}❌ Deployment verification failed${NC}" >&2
  echo "Check logs: docker compose logs" >&2
  exit 1
fi
