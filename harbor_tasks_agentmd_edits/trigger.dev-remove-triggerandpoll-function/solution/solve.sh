#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trigger.dev

# Idempotent: skip if already applied
if ! grep -q 'triggerAndPoll' packages/trigger-sdk/src/v3/shared.ts 2>/dev/null; then
    echo 'Patch already applied.'
    exit 0
fi

# 1. Remove triggerAndPoll function and its JSDoc from shared.ts (lines 496-516)
sed -i '496,516d' packages/trigger-sdk/src/v3/shared.ts

# 2. Remove triggerAndPoll from imports and exports in tasks.ts
sed -i 's/triggerAndPoll,//' packages/trigger-sdk/src/v3/tasks.ts

# 3. Remove triggerAndPoll call from sdkUsage.ts (lines 17-20)
sed -i '17,20d' references/v3-catalog/src/trigger/sdkUsage.ts

# 4. Remove triggerAndPoll row from docs/triggering.mdx table (line 14)
sed -i '14d' docs/triggering.mdx

# 5. Remove triggerAndPoll section from docs/triggering.mdx (lines 165-195)
sed -i '165,195d' docs/triggering.mdx

# 6. Remove triggerAndPoll section from .cursor/rules/writing-tasks.mdc (lines 433-456)
sed -i '433,456d' .cursor/rules/writing-tasks.mdc

# 7. Create the changeset file
mkdir -p .changeset
cat > .changeset/slow-games-drum.md << 'EOF'
---
"@trigger.dev/sdk": patch
---

Removed triggerAndPoll. It was never recommended so it's been removed.
EOF

echo 'Patch applied successfully.'
