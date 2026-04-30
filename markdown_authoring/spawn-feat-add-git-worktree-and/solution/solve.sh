#!/usr/bin/env bash
set -euo pipefail

cd /workspace/spawn

# Idempotency guard
if grep -qF "When multiple agents work in parallel, they MUST use worktrees instead of `git c" ".claude/skills/setup-trigger-service/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/setup-trigger-service/SKILL.md b/.claude/skills/setup-trigger-service/SKILL.md
@@ -227,7 +227,7 @@ printf '<secret-from-step-2>' | gh secret set <SERVICE_NAME>_TRIGGER_SECRET --re
 The target script (e.g., `refactor.sh`, `improve.sh`) MUST:
 
 1. **Run a single cycle and exit** — no `while true` loops
-2. **Sync with origin before work** — `git fetch && git reset --hard origin/main`
+2. **Sync with origin before work** — `git fetch origin main && git pull origin main`
 3. **Exit cleanly** — so the trigger server marks it as "not running" and accepts the next trigger
 
 If converting from a looping script, remove the `while true` / `sleep` and keep only the body of one iteration.
@@ -236,6 +236,65 @@ If converting from a looping script, remove the `while true` / `sleep` and keep
 - `improve.sh` — Continuous improvement loop for spawn (already single-cycle ready)
 - `refactor.sh` — Refactoring team service (already single-cycle ready)
 
+## Git Conventions for Agent Team Scripts
+
+All agent team scripts (`improve.sh`, `refactor.sh`, and any future scripts) MUST instruct their agents to follow these conventions:
+
+### 1. Always pull main before creating worktrees
+
+Agents MUST fetch and pull the latest main before starting any branch work:
+
+```bash
+git fetch origin main
+git pull origin main
+```
+
+### 2. Use git worktrees for all branch work
+
+When multiple agents work in parallel, they MUST use worktrees instead of `git checkout -b` to avoid clobbering each other's uncommitted changes:
+
+```bash
+# Fetch latest main first
+git fetch origin main
+
+# Create worktree from latest origin/main
+git worktree add /tmp/spawn-worktrees/BRANCH-NAME -b BRANCH-NAME origin/main
+
+# Work inside the worktree
+cd /tmp/spawn-worktrees/BRANCH-NAME
+# ... make changes ...
+
+# Commit, push, create PR, merge
+git push -u origin BRANCH-NAME
+gh pr create --title "..." --body "..."
+gh pr merge --squash --delete-branch
+
+# Clean up
+git worktree remove /tmp/spawn-worktrees/BRANCH-NAME
+```
+
+### 3. Include Agent markers in commits
+
+Every agent commit MUST include an `Agent:` trailer identifying which agent authored it:
+
+```
+feat: Add RunPod cloud provider
+
+Agent: cloud-scout
+Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
+```
+
+### 4. Clean up worktrees at end of cycle
+
+The team lead or cleanup function must prune stale worktrees:
+
+```bash
+git worktree prune
+rm -rf /tmp/spawn-worktrees
+```
+
+These conventions are already embedded in the prompts of `improve.sh` and `refactor.sh`. When adding new service scripts, copy the same patterns.
+
 ## Step 9: Commit and push
 
 Commit the workflow file and .gitignore changes (but NOT the wrapper script):
PATCH

echo "Gold patch applied."
