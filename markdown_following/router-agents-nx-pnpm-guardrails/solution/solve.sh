#!/usr/bin/env bash
set -euo pipefail

cd /workspace/router

# Idempotency: if the gold patch is already applied, exit early.
if grep -q 'Agent execution guardrails (important)' AGENTS.md 2>/dev/null; then
    echo "Gold patch already applied. Skipping."
    exit 0
fi

# Apply the inlined gold diff for PR TanStack/router#6671.
git apply --whitespace=nowarn /solution/gold.diff

echo "Gold patch applied to AGENTS.md."
