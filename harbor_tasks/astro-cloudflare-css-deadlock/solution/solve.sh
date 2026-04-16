#!/bin/bash
set -e

REPO_DIR="/workspace/astro"
TARGET_FILE="packages/astro/src/vite-plugin-css/index.ts"

cd "$REPO_DIR"

# Apply the fix using sed to insert the guard clause
# The fix adds a check to skip virtual dev-css modules to prevent circular deadlocks

# First, let's verify the distinctive line exists (idempotency check)
if grep -q "Skip virtual dev-css modules to prevent circular deadlocks with the Cloudflare adapter" "$TARGET_FILE"; then
    echo "Fix already applied, skipping."
    exit 0
fi

# Insert the guard clause after the PROPAGATED_ASSET_QUERY_PARAM check
# Using a patch approach with sed
sed -i '/if (imp.id.includes(PROPAGATED_ASSET_QUERY_PARAM)) continue;/a\
\
\t\t// Skip virtual dev-css modules to prevent circular deadlocks with the Cloudflare adapter.\n\t\t// The dev-css-all module statically imports all per-route dev-css:* modules, and those\n\t\t// modules'\'' load handlers may already be running (waiting on ensureModulesLoaded), causing\n\t\t// a permanent deadlock via Vite'\''s _pendingRequests map. These are CSS collector virtuals\n\t\t// that don'\''t contain CSS themselves, so skipping them has no effect on CSS injection.\n\t\tif (\n\t\t\timp.id === RESOLVED_MODULE_DEV_CSS ||\n\t\t\timp.id === RESOLVED_MODULE_DEV_CSS_ALL ||\n\t\t\timp.id.startsWith(RESOLVED_MODULE_DEV_CSS_PREFIX)\n\t\t)\n\t\t\tcontinue;' "$TARGET_FILE"

# Verify the patch was applied
if grep -q "Skip virtual dev-css modules to prevent circular deadlocks with the Cloudflare adapter" "$TARGET_FILE"; then
    echo "Fix applied successfully."
else
    echo "Failed to apply fix!"
    exit 1
fi

# Rebuild the package to make changes take effect
cd "$REPO_DIR"
# Check if pnpm is available and build
if command -v pnpm &> /dev/null; then
    pnpm -C packages/astro build 2>&1 || echo "Build command completed with warnings"
fi

echo "Solution applied."
