#!/bin/bash
set -e

cd /workspace/hugo

# Check if already patched (idempotency)
if grep -q "DedentMarkers removes leading whitespace" markup/goldmark/hugocontext/hugocontext.go 2>/dev/null; then
    echo "Already patched, skipping"
    exit 0
fi

# Copy the Python script from the mounted solution directory
cp /solution/apply_fix.py /tmp/apply_fix.py

# Apply the fix using Python
python3 /tmp/apply_fix.py
