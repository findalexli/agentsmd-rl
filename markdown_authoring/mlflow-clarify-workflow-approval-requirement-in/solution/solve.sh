#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotency guard
if grep -qF "Copilot commits require approval to trigger workflows for security reasons, whil" ".claude/skills/copilot/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/copilot/SKILL.md b/.claude/skills/copilot/SKILL.md
@@ -63,7 +63,7 @@ After sending feedback, Copilot starts a new session, typically within ~10 secon
 
 ## Approving workflows
 
-Approve workflows to run once the PR is finalized:
+Copilot commits require approval to trigger workflows for security reasons, while maintainer commits do not. Once the PR is finalized, run the approve script:
 
 ```bash
 bash .claude/skills/copilot/approve.sh "<owner>/<repo>" <pr_number>
PATCH

echo "Gold patch applied."
