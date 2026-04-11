#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotent: skip if already applied
if grep -q 'gh agent-task list' .claude/skills/copilot/poll.sh 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.claude/skills/copilot/SKILL.md b/.claude/skills/copilot/SKILL.md
index e4a231973e6b7..22a1f0d8b8dd6 100644
--- a/.claude/skills/copilot/SKILL.md
+++ b/.claude/skills/copilot/SKILL.md
@@ -3,6 +3,7 @@ name: copilot
 description: Hand off a task to GitHub Copilot.
 allowed-tools:
   - Bash(gh agent-task create:*)
+  - Bash(gh agent-task list:*)
   - Bash(gh agent-task view:*)
   - Bash(bash .claude/skills/copilot/poll.sh *)
   - Bash(gh api:*)
@@ -29,16 +30,10 @@ Example:

 ## Polling for completion

-Once Copilot starts working, extract the session ID from the output URL and poll in the background until Copilot finishes:
+Once Copilot starts working, poll in the background until Copilot finishes. The script automatically finds the latest session for the PR:

 ```bash
-# gh agent-task create returns a URL like:
-# https://github.com/mlflow/mlflow/pull/21887/agent-sessions/523bb0e1-...
-session_url=$(gh agent-task create -F task-desc.md)
-session_id="${session_url##*/}"
-
-# Poll using session ID
-bash .claude/skills/copilot/poll.sh "$session_id" "<owner>/<repo>" <pr_number>
+bash .claude/skills/copilot/poll.sh "<owner>/<repo>" <pr_number>
 ```

 ## Sending feedback
diff --git a/.claude/skills/copilot/poll.sh b/.claude/skills/copilot/poll.sh
index 5c27e7cffa729..dc7cd51606e31 100755
--- a/.claude/skills/copilot/poll.sh
+++ b/.claude/skills/copilot/poll.sh
@@ -1,11 +1,23 @@
 #!/usr/bin/env bash
 set -euo pipefail

-session_id="$1"
-repo="$2"        # owner/repo format
-pr_number="$3"
+repo="$1"        # owner/repo format
+pr_number="$2"
 max_seconds=1800  # 30 minutes

+# Find the latest session for this PR
+session_id=$(
+  gh agent-task list \
+    --json id,pullRequestNumber,createdAt,repository \
+    --jq "
+      [.[] | select(.repository == \"${repo}\" and .pullRequestNumber == ${pr_number})]
+      | sort_by(.createdAt)
+      | last
+      | .id
+    "
+)
+echo "Polling session $session_id for PR #${pr_number}"
+
 while true; do
   if (( SECONDS > max_seconds )); then
     echo "Timed out after ${max_seconds}s waiting for Copilot to finish"

PATCH

echo "Patch applied successfully."
