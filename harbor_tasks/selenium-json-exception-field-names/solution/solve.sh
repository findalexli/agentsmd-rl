#!/bin/bash
set -e

cd /workspace/selenium

# Apply the gold patch for PR #17225
git apply /solution/pr17225.patch

echo "Patch applied successfully"
