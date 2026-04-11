#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotent: skip if already applied
if [ -f ".github/skills/integration-tests/SKILL.md" ]; then
    echo "Patch already applied."
    exit 0
fi

# Fetch merge commit and its parent to get the diff
git fetch origin c065b175fdbadc9fc204d668ccdd8e7e0155c63b --depth=2

# Get the diff of the merge commit
git diff HEAD..c065b175fdbadc9fc204d668ccdd8e7e0155c63b > /tmp/patch.diff

# Apply the patch
git apply /tmp/patch.diff

echo "Patch applied successfully."
