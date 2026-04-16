#!/bin/bash
set -e

cd /workspace/kotlin

# Apply the fix using Python script
python3 /solution/apply_fix.py

echo "Patch applied successfully!"
