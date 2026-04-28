#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slack-gamebot

# Idempotency guard
if grep -qF "git branch --merged master | grep -v '^\\* \\|^  master$' | xargs -r git branch -d" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,5 +1,15 @@
 # AI Agent Instructions
 
+## Starting Work
+
+Before creating a new branch, always sync and clean up:
+
+```
+git checkout master
+git pull
+git branch --merged master | grep -v '^\* \|^  master$' | xargs -r git branch -d
+```
+
 ## After Making Code Changes
 
 Always run the following commands before committing:
@@ -29,4 +39,5 @@ Update [CHANGELOG.md](CHANGELOG.md) for any user-facing change. Add a line at th
 
 ## Commits and PRs
 
+- Never push directly to master — always work on a branch and open a PR.
 - Squash commits before merging — one logical commit per PR.
PATCH

echo "Gold patch applied."
