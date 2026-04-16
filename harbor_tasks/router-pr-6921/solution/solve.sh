#!/bin/bash
set -e

cd /workspace/router

# Check if already applied (idempotency)
if grep -q "LoaderStaleReloadMode" packages/router-core/src/route.ts 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Download fixed files from the merge commit
MERGE_COMMIT="6f297a249424c0fd1c1a56aa4fc12c8217be7b6a"
BASE_URL="https://raw.githubusercontent.com/TanStack/router/${MERGE_COMMIT}"

# Download and replace the key files
curl -sL "${BASE_URL}/packages/router-core/src/route.ts" -o packages/router-core/src/route.ts
curl -sL "${BASE_URL}/packages/router-core/src/router.ts" -o packages/router-core/src/router.ts
curl -sL "${BASE_URL}/packages/router-core/src/load-matches.ts" -o packages/router-core/src/load-matches.ts
curl -sL "${BASE_URL}/packages/router-core/src/index.ts" -o packages/router-core/src/index.ts
curl -sL "${BASE_URL}/packages/router-core/tests/load.test.ts" -o packages/router-core/tests/load.test.ts

# Rebuild the package
pnpm nx run @tanstack/router-core:build --skip-nx-cache

echo "Patch applied successfully"
