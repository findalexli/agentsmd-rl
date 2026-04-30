#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ethskills

# Idempotency guard
if grep -qF "- **SE2 Skill:** https://docs.scaffoldeth.io/SKILL.md" "orchestration/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/orchestration/SKILL.md b/orchestration/SKILL.md
@@ -220,5 +220,6 @@ packages/
 ## Resources
 
 - **SE2 Docs:** https://docs.scaffoldeth.io/
+- **SE2 Skill:** https://docs.scaffoldeth.io/SKILL.md
 - **UI Components:** https://ui.scaffoldeth.io/
 - **SE2 AGENTS.md:** https://github.com/scaffold-eth/scaffold-eth-2/blob/main/AGENTS.md
PATCH

echo "Gold patch applied."
