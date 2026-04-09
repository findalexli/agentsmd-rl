#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -A 10 'const press = defineTabTool' packages/playwright/src/mcp/browser/tools/keyboard.ts 2>/dev/null | grep -q "if (params.key === 'Enter')"; then
    echo "Patch already applied."
    exit 0
fi

python3 /solution/apply_fix.py

echo "Fix applied successfully."
