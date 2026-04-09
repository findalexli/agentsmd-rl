#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch from the PR diff
git apply /solution/pr.diff

# Verify the patch was applied by checking for a distinctive line
grep -q "System transactions are always accepted" crates/sui-core/src/consensus_types/consensus_output_api.rs && echo "Patch applied successfully"
