#!/bin/bash
set -e

cd /workspace/tanstack-router

# Idempotency check: skip if fix already applied
if grep -q "export const isRolldown" packages/start-plugin-core/src/utils.ts 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Fetch the merge commit
git fetch origin 6651473d028a55c70f3f54af37a12b4379b46813 --depth=1

# Checkout the specific files from the merge commit
git checkout 6651473d028a55c70f3f54af37a12b4379b46813 -- \
    packages/start-plugin-core/src/utils.ts \
    packages/start-plugin-core/src/plugin.ts \
    packages/start-plugin-core/src/preview-server-plugin/plugin.ts

# Create the changeset directory and file
mkdir -p .changeset
cat > .changeset/rolldownoptions-compat.md <<'EOF'
---
'@tanstack/start-plugin-core': minor
---

Support both Vite 7 (`rollupOptions`) and Vite 8 (`rolldownOptions`) by detecting the Vite version at runtime
EOF

echo "Patch applied successfully."
