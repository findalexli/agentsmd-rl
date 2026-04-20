#!/bin/bash
set -e

cd /workspace/quickwit

# Use Python to apply patches (avoids git apply issues with heredocs)
python3 /solution/apply_patch.py

echo "Solution applied successfully"