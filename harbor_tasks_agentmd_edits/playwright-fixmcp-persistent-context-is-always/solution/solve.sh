#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'config.browser.userDataDir' packages/playwright-core/src/mcp/program.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply gold patch (stored alongside this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
git apply --whitespace=fix "$SCRIPT_DIR/gold.patch"

echo "Patch applied successfully."
