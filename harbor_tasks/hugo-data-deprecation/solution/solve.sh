#!/bin/bash
set -e

cd /workspace/hugo

# Check if already applied (idempotency)
if grep -q "printSiteDataDeprecationInit" hugolib/hugo_sites.go; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the fix using Python script (avoiding patch whitespace issues)
python3 /solution/apply_fix.py

echo "Patch applied successfully"
