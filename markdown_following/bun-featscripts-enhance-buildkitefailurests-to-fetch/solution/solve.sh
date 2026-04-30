#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'Debugging CI Failures' CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fetch the merge commit and checkout both changed files
git fetch origin 7e9fa4ab08d9250c72795565c173cf7349de4018 --depth=1
git checkout 7e9fa4ab08d9250c72795565c173cf7349de4018 -- scripts/buildkite-failures.ts CLAUDE.md

echo "Patch applied successfully."
