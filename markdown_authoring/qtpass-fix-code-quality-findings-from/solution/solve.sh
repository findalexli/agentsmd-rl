#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qtpass

# Idempotency guard
if grep -qF "# Use an unresolved thread ID from step 1 output (format typically starts with P" ".opencode/skills/qtpass-github/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.opencode/skills/qtpass-github/SKILL.md b/.opencode/skills/qtpass-github/SKILL.md
@@ -47,7 +47,7 @@ gh pr create --base main --title "Fix" --body "Fixes #issue"
 **Before pushing or merging, always update with latest main:**
 
 ```bash
-# (If not already set) add upstream remote pointing to main repository
+# If upstream remote is not set, add it (one-time setup):
 git remote add upstream https://github.com/IJHack/QtPass.git
 # Fetch and rebase on main
 git fetch upstream
@@ -369,7 +369,8 @@ gh api graphql -f query='{ repository(owner: "<owner>", name: "<repo>") { pullRe
 
 ```bash
 # Get thread IDs and resolve them
-THREAD_ID="PRRT_xxx"
+# Use an unresolved thread ID from step 1 output (format typically starts with PRRT_)
+THREAD_ID="PRRT_FROM_STEP_1"
 gh api graphql -f query="mutation { resolveReviewThread(input: {threadId: \"$THREAD_ID\"}) { thread { isResolved } } }"
 ```
 
PATCH

echo "Gold patch applied."
