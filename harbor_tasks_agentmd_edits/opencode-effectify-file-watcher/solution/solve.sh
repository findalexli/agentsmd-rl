#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied (check for Effect callback doc in AGENTS.md)
if grep -q "Effect.callback" packages/opencode/AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the full patch from the solution directory
git apply - --whitespace=fix < /workspace/solution/full.patch

echo "Patch applied successfully."
