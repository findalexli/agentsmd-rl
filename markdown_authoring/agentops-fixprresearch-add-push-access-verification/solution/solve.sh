#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agentops

# Idempotency guard
if grep -qF "**Unless `viewerPermission` is `ADMIN` or `WRITE`, assume fork-based workflow is" "plugins/pr-kit/skills/pr-research/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/pr-kit/skills/pr-research/SKILL.md b/plugins/pr-kit/skills/pr-research/SKILL.md
@@ -482,6 +482,38 @@ Next: /pr-plan ~/gt/.agents/<rig>/research/YYYY-MM-DD-pr-{repo}.md
 | Start with large PRs | Begin with small, focused changes |
 | Assume conventions | Check commit message style |
 | Ignore issue labels | Look for "good first issue" |
+| **Assume push access** | **Always verify with `gh repo view --json viewerPermission`** |
+
+---
+
+## Push Access Verification
+
+**CRITICAL**: Never assume the user has push access to external repositories.
+
+### Check Access Level
+
+```bash
+# Verify actual permissions
+gh repo view <owner/repo> --json viewerPermission --jq '.viewerPermission'
+```
+
+| Permission | Meaning | Workflow |
+|------------|---------|----------|
+| `ADMIN` | Owner/admin | Can push directly |
+| `WRITE` | Collaborator | Can push directly |
+| `READ` | Read-only | **Must fork and PR** |
+| `NONE` | No access | **Must fork and PR** |
+
+### Default Assumption
+
+**Unless `viewerPermission` is `ADMIN` or `WRITE`, assume fork-based workflow is required.**
+
+Do NOT tell users they have push access based on:
+- Being "crew" or having a local clone
+- The repo being in their workspace
+- Any assumption about their role
+
+**Always verify programmatically.**
 
 ---
 
PATCH

echo "Gold patch applied."
