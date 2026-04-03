#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'serializeSearch' packages/route-pattern/src/lib/route-pattern/serialize.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch (squash merge commit, parent is our base)
git cherry-pick --no-commit 87447287f87d29f394c71c1859d293f78b69cdca

echo "Patch applied successfully."
