#!/bin/bash
set -e

cd /workspace/router

# Apply the gold patch for PR #6897: improve github release changelog
git apply /solution/fix.patch

echo "Patch applied successfully"
