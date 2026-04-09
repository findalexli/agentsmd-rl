#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dummy-repo

# Fix the broken_add function
sed -i 's/return a  # Bug: ignores b/return a + b  # Fixed/' math_ops.py

echo "Patch applied successfully."
