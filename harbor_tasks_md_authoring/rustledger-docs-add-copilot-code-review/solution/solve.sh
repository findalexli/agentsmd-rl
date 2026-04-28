#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rustledger

# Idempotency guard
if grep -qF "This triggers a fresh review against the current diff. Copilot leaves \"Comment\" " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -170,6 +170,16 @@ PRs can auto-merge after CI passes if:
 - PR is not marked as draft
 - No merge conflicts
 
+### Requesting Copilot Code Review
+
+Request or re-request a Copilot review on any PR:
+
+```bash
+gh pr edit <PR_NUMBER> --add-reviewer @copilot
+```
+
+This triggers a fresh review against the current diff. Copilot leaves "Comment" reviews (never approves or blocks merging).
+
 ### Using GLM5 for PR Reviews
 
 You can use [opencode](https://opencode.ai) with Together AI's GLM-5 model for additional PR review perspectives.
PATCH

echo "Gold patch applied."
