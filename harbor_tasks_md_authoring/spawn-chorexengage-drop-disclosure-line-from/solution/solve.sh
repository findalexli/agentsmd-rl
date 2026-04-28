#!/usr/bin/env bash
set -euo pipefail

cd /workspace/spawn

# Idempotency guard
if grep -qF "- **NO disclosure line.** Do not add \"(disclosure: i help build this)\" or any si" ".claude/skills/setup-agent-team/x-engage-prompt.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/setup-agent-team/x-engage-prompt.md b/.claude/skills/setup-agent-team/x-engage-prompt.md
@@ -36,7 +36,7 @@ X_DATA_PLACEHOLDER
    - NO bulleted lists, NO multi-sentence explanations, NO feature dumps
    - Include the link `https://openrouter.ai/spawn` ONLY if it naturally closes the reply
    - **NEVER use em dashes (—) or en dashes (–).** Use periods, commas, or rephrase.
-   - Add "(disclosure: i help build this)" ONLY if it fits — if the reply is too short, skip disclosure entirely
+   - **NO disclosure line.** Do not add "(disclosure: i help build this)" or any similar attribution. Post the reply as-is.
 
 4. **If no good engagement opportunity** (all scores < 7), output `found: false`.
 
PATCH

echo "Gold patch applied."
