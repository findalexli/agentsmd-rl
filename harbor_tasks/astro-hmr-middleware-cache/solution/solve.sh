#!/bin/bash
set -e

cd /workspace/astro

# Check if already applied
if grep -q "clearMiddleware(): void" packages/astro/src/core/base-pipeline.ts 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the fix using Python
python3 /solution/apply_fix.py

echo "Fix applied successfully!"
