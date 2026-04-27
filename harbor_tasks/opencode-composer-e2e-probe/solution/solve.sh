#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency guard: if patch already applied, exit cleanly.
if [ -f packages/app/src/testing/session-composer.ts ] \
   && grep -q 'opencode:e2e:composer' packages/app/src/testing/session-composer.ts; then
    echo "Gold patch already applied."
    exit 0
fi

# Apply the inlined gold patch shipped alongside this script.
git apply --whitespace=nowarn /solution/gold.patch
echo "Gold patch applied."
