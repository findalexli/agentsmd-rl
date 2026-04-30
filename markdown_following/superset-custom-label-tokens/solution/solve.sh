#!/bin/bash
set -euo pipefail

cd /workspace/superset

# Idempotency: skip if the gold patch is already applied
if grep -q "labelPublishedColor" superset-frontend/packages/superset-core/src/theme/types.ts 2>/dev/null; then
  echo "Patch already applied"
  exit 0
fi

git apply --whitespace=nowarn /solution/gold-source.patch
echo "Gold patch applied successfully"
