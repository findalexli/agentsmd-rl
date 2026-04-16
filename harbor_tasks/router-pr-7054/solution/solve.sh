#!/bin/bash
set -e

cd /workspace/router

# Idempotency check - skip if patch already applied
# Look for the specific useLayoutEffect call in OnRendered function that was added by the fix
if grep -q "useLayoutEffect(() =>" packages/react-router/src/Match.tsx 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch from the diff file
git apply --verbose /solution/pr7054.diff

echo "Patch applied successfully."

# Rebuild the affected packages
pnpm nx run @tanstack/react-router:build --skip-nx-cache
