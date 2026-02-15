#!/bin/bash

# =============================================================================
# OpenClaw Docker Deployment Verification Script
# =============================================================================
# This script verifies that OpenClaw is deployed securely and correctly.
# Run this after deployment: ./verify.sh
# =============================================================================

set -e

echo "🔍 OpenClaw Docker Deployment Verification"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    PASSED=$((PASSED + 1))
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    FAILED=$((FAILED + 1))
}

warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
    WARNINGS=$((WARNINGS + 1))
}

info() {
    echo -e "ℹ️  INFO: $1"
}

# Check 1: Container is running
echo "1. Checking if OpenClaw container is running..."
if docker ps | grep -q openclaw; then
    pass "OpenClaw container is running"
else
    fail "OpenClaw container is not running"
    echo "   Run: docker-compose up -d"
fi
echo ""

# Check 2: Version is safe (>= 2026.1.29)
echo "2. Checking OpenClaw version (must be >= 2026.1.29 to patch CVEs)..."
VERSION=$(docker exec openclaw openclaw --version 2>/dev/null || echo "unknown")
if echo "$VERSION" | grep -qE '2026\.1\.(29|[3-9][0-9])'; then
    pass "OpenClaw version is safe: $VERSION"
else
    fail "OpenClaw version is unsafe or unknown: $VERSION"
    echo "   Must be version 2026.1.29 or later to patch CVE-2026-25253 and CVE-2026-24763"
fi
echo ""

# Check 3: No ports exposed to 0.0.0.0
echo "3. Checking that no ports are exposed to 0.0.0.0..."
EXPOSED_PORTS=$(docker ps --filter "name=openclaw" --format "{{.Ports}}" | grep -o '0.0.0.0:[0-9]*' || true)
if [ -z "$EXPOSED_PORTS" ]; then
    pass "No ports exposed to 0.0.0.0 (Shodan-safe)"
else
    fail "Ports exposed to 0.0.0.0: $EXPOSED_PORTS"
    echo "   This is CRITICAL - Shodan will find port 18789!"
fi
echo ""

# Check 4: Health check status
echo "4. Checking container health status..."
HEALTH=$(docker inspect openclaw | jq -r '.[0].State.Health.Status' 2>/dev/null || echo "unknown")
if [ "$HEALTH" = "healthy" ]; then
    pass "Container health check: $HEALTH"
elif [ "$HEALTH" = "starting" ]; then
    warn "Container health check: $HEALTH (still starting)"
else
    fail "Container health check: $HEALTH"
fi
echo ""

# Check 5: Network is internal
echo "5. Checking network isolation..."
INTERNAL=$(docker network inspect openclaw_openclaw_net | jq -r '.[0].Internal' 2>/dev/null || echo "false")
if [ "$INTERNAL" = "true" ]; then
    pass "Network is internal (no public internet access)"
else
    fail "Network is not internal"
fi
echo ""

# Check 6: Read-only filesystem
echo "6. Checking filesystem security..."
READONLY=$(docker inspect openclaw | jq -r '.[0].HostConfig.ReadonlyRootfs' 2>/dev/null || echo "false")
if [ "$READONLY" = "true" ]; then
    pass "Filesystem is read-only (security hardening applied)"
else
    warn "Filesystem is not read-only (security hardening missing)"
fi
echo ""

# Check 7: Resource usage
echo "7. Checking resource usage..."
CPU=$(docker stats openclaw --no-stream --format "{{.CPUPerc}}" 2>/dev/null || echo "N/A")
MEM=$(docker stats openclaw --no-stream --format "{{.MemUsage}}" 2>/dev/null || echo "N/A")
info "CPU: $CPU, Memory: $MEM"
echo ""

# Check 8: No error logs
echo "8. Checking logs for errors..."
ERRORS=$(docker-compose logs openclaw 2>/dev/null | grep -i error | wc -l || echo "0")
if [ "$ERRORS" -eq 0 ]; then
    pass "No errors found in logs"
else
    warn "Found $ERRORS error(s) in logs"
    echo "   Run: docker-compose logs openclaw | grep -i error"
fi
echo ""

# Check 9: Volumes mounted
echo "9. Checking persistent volumes..."
VOLUMES=$(docker inspect openclaw | jq -r '.[0].Mounts | length' 2>/dev/null || echo "0")
if [ "$VOLUMES" -ge 2 ]; then
    pass "Persistent volumes mounted: $VOLUMES volumes"
else
    warn "Only $VOLUMES volume(s) mounted (expected at least 2)"
fi
echo ""

# Check 10: Security options
echo "10. Checking security hardening options..."
NO_NEW_PRIVS=$(docker inspect openclaw | jq -r '.[0].HostConfig.SecurityOpt' | grep -c 'no-new-privileges' || echo "0")
if [ "$NO_NEW_PRIVS" -gt 0 ]; then
    pass "Security options applied (no-new-privileges)"
else
    warn "Security options not fully applied"
fi
echo ""

# Summary
echo "=========================================="
echo "Summary:"
echo "  Passed:  $PASSED"
echo "  Failed:  $FAILED"
echo "  Warnings: $WARNINGS"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All critical checks passed!${NC}"
    echo ""
    echo "OpenClaw is deployed securely."
    echo ""
    echo "Next steps:"
    echo "  1. Access OpenClaw: docker exec -it openclaw bash"
    echo "  2. Run OpenClaw: docker exec -it openclaw openclaw"
    echo "  3. View logs: docker-compose logs -f openclaw"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Please review and fix.${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. View logs: docker-compose logs openclaw"
    echo "  2. Restart: docker-compose restart"
    echo "  3. Redeploy: docker-compose down && docker-compose up -d"
    exit 1
fi
