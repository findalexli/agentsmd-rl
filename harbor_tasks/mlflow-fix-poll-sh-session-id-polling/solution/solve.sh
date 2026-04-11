#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotent: skip if already applied
if grep -q 'session_id="\$1"' .claude/skills/copilot/poll.sh 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.claude/skills/copilot/SKILL.md b/.claude/skills/copilot/SKILL.md
index eec366f14d99a..e4a231973e6b7 100644
--- a/.claude/skills/copilot/SKILL.md
+++ b/.claude/skills/copilot/SKILL.md
@@ -3,6 +3,7 @@ name: copilot
 description: Hand off a task to GitHub Copilot.
 allowed-tools:
   - Bash(gh agent-task create:*)
+  - Bash(gh agent-task view:*)
   - Bash(bash .claude/skills/copilot/poll.sh *)
   - Bash(gh api:*)
 ---
@@ -28,10 +29,16 @@ Example:

 ## Polling for completion

-Once Copilot starts working, poll in the background until Copilot finishes:
+Once Copilot starts working, extract the session ID from the output URL and poll in the background until Copilot finishes:

 ```bash
-bash .claude/skills/copilot/poll.sh <owner>/<repo> <pr_number>
+# gh agent-task create returns a URL like:
+# https://github.com/mlflow/mlflow/pull/21887/agent-sessions/523bb0e1-...
+session_url=$(gh agent-task create -F task-desc.md)
+session_id="${session_url##*/}"
+
+# Poll using session ID
+bash .claude/skills/copilot/poll.sh "$session_id" "<owner>/<repo>" <pr_number>
 ```

 ## Sending feedback
diff --git a/.claude/skills/copilot/poll.sh b/.claude/skills/copilot/poll.sh
index 084cc48ed1a4a..5c27e7cffa729 100755
--- a/.claude/skills/copilot/poll.sh
+++ b/.claude/skills/copilot/poll.sh
@@ -1,8 +1,9 @@
 #!/usr/bin/env bash
 set -euo pipefail

-repo="$1"        # owner/repo format (e.g., mlflow/mlflow)
-pr_number="$2"
+session_id="$1"
+repo="$2"        # owner/repo format
+pr_number="$3"
 max_seconds=1800  # 30 minutes

 while true; do
@@ -10,11 +11,9 @@ while true; do
     echo "Timed out after ${max_seconds}s waiting for Copilot to finish"
     exit 1
   fi
-  result=$(gh api "repos/${repo}/issues/${pr_number}/timeline" \
-    --paginate \
-    --jq '.[] | select(.event == "copilot_work_finished") | .created_at')
-  if [[ -n "$result" ]]; then
-    echo "Copilot finished at $result"
+  state=$(gh agent-task view "$session_id" --json state --jq '.state')
+  if [[ "$state" != "queued" && "$state" != "in_progress" ]]; then
+    echo "Copilot finished with state: $state"
     break
   fi
   sleep 30

PATCH

echo "Patch applied successfully."
