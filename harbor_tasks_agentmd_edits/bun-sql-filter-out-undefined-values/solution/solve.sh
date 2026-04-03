#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'buildDefinedColumnsAndQuery' src/js/internal/sql/shared.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fetch and apply the PR diff
curl -sL "https://github.com/oven-sh/bun/pull/25830.diff" | git apply --whitespace=fix -

echo "Patch applied successfully."
