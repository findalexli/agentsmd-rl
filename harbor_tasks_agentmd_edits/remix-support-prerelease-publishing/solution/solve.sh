#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'readRemixPrereleaseConfig' scripts/utils/changes.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fetch the merge commit and apply the diff
git fetch origin 3dbc5db1478ca25170211e89288a48a66e025a65 --depth=1
git diff ecb2847dea0dcebb0972c8de23cdfa661483745e..3dbc5db1478ca25170211e89288a48a66e025a65 | git apply --whitespace=fix -

echo "Patch applied successfully."
