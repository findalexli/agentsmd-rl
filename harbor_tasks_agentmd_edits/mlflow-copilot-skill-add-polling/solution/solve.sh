#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotent: skip if already applied
if [ -f .claude/skills/copilot/poll.sh ]; then
    echo "Patch already applied."
    exit 0
fi

# Create poll.sh
cat > .claude/skills/copilot/poll.sh <<'POLLSCRIPT'
#!/usr/bin/env bash
set -euo pipefail

repo="$1"        # owner/repo format (e.g., mlflow/mlflow)
pr_number="$2"
max_seconds=1800  # 30 minutes

while true; do
  if (( SECONDS > max_seconds )); then
    echo "Timed out after ${max_seconds}s waiting for Copilot to finish"
    exit 1
  fi
  result=$(gh api "repos/${repo}/issues/${pr_number}/timeline" \
    --paginate \
    --jq '.[] | select(.event == "copilot_work_finished") | .created_at')
  if [[ -n "$result" ]]; then
    echo "Copilot finished at $result"
    break
  fi
  sleep 30
done
POLLSCRIPT
chmod +x .claude/skills/copilot/poll.sh

# Update SKILL.md: add poll.sh to allowed-tools and add polling section
git apply - <<'PATCH'
diff --git a/.claude/skills/copilot/SKILL.md b/.claude/skills/copilot/SKILL.md
index 4c768a6c85dc4..3d6aff3fbceca 100644
--- a/.claude/skills/copilot/SKILL.md
+++ b/.claude/skills/copilot/SKILL.md
@@ -3,6 +3,7 @@ name: copilot
 description: Hand off a task to GitHub Copilot.
 allowed-tools:
   - Bash(gh agent-task create:*)
+  - Bash(bash .claude/skills/copilot/poll.sh *)
 ---

 ## Examples
@@ -23,3 +24,11 @@ Example:

 - Session: https://github.com/mlflow/mlflow/pull/20905/agent-sessions/abc123
 - PR: https://github.com/mlflow/mlflow/pull/20905
+
+## Polling for completion
+
+Once Copilot starts working, poll in the background until Copilot finishes:
+
+```bash
+bash .claude/skills/copilot/poll.sh {owner}/{repo} {pr_number}
+```

PATCH

echo "Patch applied successfully."
