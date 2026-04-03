#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotent: skip if already applied
if [ -f ".github/skills/integration-tests/SKILL.md" ]; then
    echo "Patch already applied."
    exit 0
fi

# Fetch the merge commit and cherry-pick it (squash-merged, single parent)
git fetch origin c065b175fdbadc9fc204d668ccdd8e7e0155c63b --depth=1
git cherry-pick --no-commit FETCH_HEAD

echo "Patch applied successfully."
