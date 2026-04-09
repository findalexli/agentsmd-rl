#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied
if grep -q "### Benchmarking" README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fetch the merge commit and apply the diff
git fetch origin f640f66dda0885ee903ff64b01a614c2d3fe0807 2>&1
git diff 6a122196c2696fa971bcd9da5a92da739df5c9cf..f640f66dda0885ee903ff64b01a614c2d3fe0807 | git apply -

echo "Patch applied successfully."
