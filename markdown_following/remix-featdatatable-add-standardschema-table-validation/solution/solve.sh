#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q "Cross-package boundaries" AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fetch the merge commit
git fetch origin 28d74aae012ca78b82fedaf6f7f5de53094fd002 --depth=1

# Checkout files directly from the merge commit (avoiding cherry-pick conflicts)
git checkout 28d74aae012ca78b82fedaf6f7f5de53094fd002 -- AGENTS.md
git checkout 28d74aae012ca78b82fedaf6f7f5de53094fd002 -- packages/data-table/README.md
git checkout 28d74aae012ca78b82fedaf6f7f5de53094fd002 -- packages/data-table/src/index.ts

git checkout 28d74aae012ca78b82fedaf6f7f5de53094fd002 -- packages/data-table/src/lib/database.ts
git checkout 28d74aae012ca78b82fedaf6f7f5de53094fd002 -- packages/data-table/src/lib/table.test.ts
git checkout 28d74aae012ca78b82fedaf6f7f5de53094fd002 -- packages/data-table/src/lib/table.ts

# Stage all changes
git add -A

# Run pnpm install to ensure deps are available
corepack enable pnpm
pnpm install --frozen-lockfile --ignore-scripts

# Run prettier formatting on the changed file
pnpm prettier --write packages/data-table/src/lib/table.ts

echo "Patch applied successfully."
