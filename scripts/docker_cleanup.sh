#!/usr/bin/env bash
# Periodic docker cleanup to prevent disk exhaustion during batch task creation.
# Run this between batches of docker builds.
set -euo pipefail

echo "=== Docker disk usage before cleanup ==="
docker system df 2>/dev/null

# Remove stopped containers
docker container prune -f 2>/dev/null || true

# Remove dangling images (untagged)
docker image prune -f 2>/dev/null || true

# Remove unused build cache older than 1h
docker builder prune -f --filter "until=1h" 2>/dev/null || true

echo ""
echo "=== Docker disk usage after cleanup ==="
docker system df 2>/dev/null

# Check available disk space
AVAIL=$(df -BG / | tail -1 | awk '{print $4}' | tr -d 'G')
echo ""
echo "Available disk space: ${AVAIL}GB"
if [ "$AVAIL" -lt 50 ]; then
    echo "WARNING: Low disk space! Consider running: docker system prune -af"
fi
