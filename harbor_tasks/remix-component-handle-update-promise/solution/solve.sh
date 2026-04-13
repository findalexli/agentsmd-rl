#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q MAX_CASCADING_UPDATES packages/component/src/lib/scheduler.ts 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

python3 /tmp/solve.py
