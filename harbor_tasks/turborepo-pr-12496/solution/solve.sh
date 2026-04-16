#!/bin/bash
set -e

cd /workspace/turborepo

# Fetch the patch from GitHub and apply it
curl -sL "https://patch-diff.githubusercontent.com/raw/vercel/turborepo/pull/12496.patch" | git apply

# Verify the patch was applied by checking for a distinctive line
if [ -f packages/turbo-codemod/src/commands/migrate/steps/update-catalog.ts ]; then
    if grep -q "Detect if turbo is installed via a" packages/turbo-codemod/src/commands/migrate/steps/update-catalog.ts 2>/dev/null; then
        echo "Patch applied successfully"
    else
        echo "ERROR: update-catalog.ts exists but does not contain expected content"
        exit 1
    fi
else
    echo "ERROR: update-catalog.ts was not created"
    exit 1
fi

# Rebuild the codemod package
cd packages/turbo-codemod && pnpm build