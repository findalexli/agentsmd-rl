#!/bin/bash
set -e
cd /workspace/continue

# Apply the gold patch
git apply /solution/gold.patch

# Verify the patch was applied by checking for distinctive line
grep -q "const contextLength" core/config/yaml/models.ts
