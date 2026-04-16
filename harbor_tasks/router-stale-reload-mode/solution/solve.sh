#!/bin/bash
set -e

cd /workspace/router

# Check if patch was already applied (idempotency)
if grep -q "shouldReloadInBackground" packages/router-core/src/load-matches.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Download and apply the full PR patch
curl -sL "https://github.com/TanStack/router/pull/6921.patch" -o /tmp/pr6921.patch

# Apply the patch
patch -p1 < /tmp/pr6921.patch

echo "Patch applied successfully"
