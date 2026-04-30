#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if [ -f compiler/CLAUDE.md ] 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fetch the merge commit and apply changes
git fetch --depth=1 origin 03613cd68c9e1d7ec5cb1eceb91f27f1935a7b8b
git checkout FETCH_HEAD -- \
    compiler/.claude/settings.json \
    compiler/.gitignore \
    compiler/CLAUDE.md \
    compiler/packages/snap/src/constants.ts \
    compiler/packages/snap/src/fixture-utils.ts \
    compiler/packages/snap/src/runner-watch.ts \
    compiler/packages/snap/src/runner.ts

echo "Patch applied successfully."
