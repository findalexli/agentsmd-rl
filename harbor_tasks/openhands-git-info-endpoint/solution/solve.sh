#!/bin/bash
set -e

cd /workspace/openhands

# Apply the gold patch for the user git info endpoint feature
cat /solution/pr13787.diff | git apply -

echo "Patch applied successfully"
