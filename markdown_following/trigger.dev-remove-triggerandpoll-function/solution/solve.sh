#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trigger.dev

# Idempotent: skip if already applied
if ! grep -q 'triggerAndPoll' packages/trigger-sdk/src/v3/shared.ts 2>/dev/null; then
    echo 'Patch already applied.'
    exit 0
fi

# Delete from bottom to top so line numbers don't shift:

# 1. Remove triggerAndPoll section from .cursor/rules/writing-tasks.mdc (lines 434-455)
sed -i '434,455d' .cursor/rules/writing-tasks.mdc

# 2. Remove triggerAndPoll section from docs/triggering.mdx (lines 165-198)
sed -i '165,198d' docs/triggering.mdx

# 3. Remove triggerAndPoll row from docs/triggering.mdx table (line 14)
sed -i '14d' docs/triggering.mdx

# 4. Remove triggerAndPoll call from sdkUsage.ts (lines 17-20)
sed -i '17,20d' references/v3-catalog/src/trigger/sdkUsage.ts

# 5. Remove triggerAndPoll from imports and exports in tasks.ts
sed -i 's/triggerAndPoll,//' packages/trigger-sdk/src/v3/tasks.ts

# 6. Remove triggerAndPoll function and its JSDoc from shared.ts (lines 493-517)
sed -i '493,517d' packages/trigger-sdk/src/v3/shared.ts

# 7. Create the changeset file
mkdir -p .changeset
cat > .changeset/slow-games-drum.md << 'EOF'
---
"@trigger.dev/sdk": patch
---

Removed triggerAndPoll. It was never recommended so it's been removed.
EOF

# 8. Format modified files with prettier
cd /workspace/trigger.dev && npx --yes prettier@3.0.0 --write packages/trigger-sdk/src/v3/shared.ts packages/trigger-sdk/src/v3/tasks.ts references/v3-catalog/src/trigger/sdkUsage.ts 2>/dev/null || true

echo 'Patch applied successfully.'
