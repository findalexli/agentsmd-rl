#!/usr/bin/env bash
set -euo pipefail

cd /workspace/awesome-copilot

# Idempotency guard
if grep -qF "gh pr review 123 --approve \\" "skills/gh-cli/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/gh-cli/SKILL.md b/skills/gh-cli/SKILL.md
@@ -1148,9 +1148,8 @@ gh pr comment 123 --delete 456789
 gh pr review 123
 
 # Approve PR
-gh pr review 123 --approve
-
---approve-body "LGTM!"
+gh pr review 123 --approve \
+  --approve-body "LGTM!"
 
 # Request changes
 gh pr review 123 --request-changes \
PATCH

echo "Gold patch applied."
