#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'Cross-package boundaries' AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fetch the squash-merge commit and cherry-pick it
git fetch origin 28d74aae012ca78b82fedaf6f7f5de53094fd002 --depth=1
git cherry-pick --no-commit 28d74aae012ca78b82fedaf6f7f5de53094fd002

echo "Patch applied successfully."
