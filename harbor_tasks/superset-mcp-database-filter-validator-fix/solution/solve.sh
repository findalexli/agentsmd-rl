#!/bin/bash
set -e

cd /workspace/superset

# Ensure we're at the correct base commit
git checkout 81c4b126e9f7c3d0533dbc15a90b8d45db106a87 -f || true

# Apply both commits - first the field validators, then the timezone fixes
git show fc8c06f7a3ba4c0a5feeafbb522b876b5f017d45 | git apply
git show be7e1abd8ad3657337840384878d3bbe9f6bde1b | git apply

echo "Patch applied successfully"
