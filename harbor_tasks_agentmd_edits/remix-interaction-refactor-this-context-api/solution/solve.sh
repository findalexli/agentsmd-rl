#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'class InteractionHandle' packages/interaction/src/lib/interaction.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fetch the merge commit and cherry-pick it
git fetch origin e3f244b484622a0f6be1b1f215a4153474e96806 --depth=1
git cherry-pick --no-commit FETCH_HEAD

echo "Patch applied successfully."
