#!/usr/bin/env bash
set -euo pipefail

cd /workspace/example-repo

# Fix the bug: change a - b to a + b
sed -i 's/return a - b/return a + b/' calculator.py

# Verify the fix
git diff
echo "Patch applied successfully."
