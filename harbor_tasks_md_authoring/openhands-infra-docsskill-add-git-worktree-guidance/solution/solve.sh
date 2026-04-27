#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openhands-infra

# Idempotency guard
if grep -qF "**Use git worktrees** to work on features, bug fixes, docs, or any git commits/P" ".claude/skills/github-workflow/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/github-workflow/SKILL.md b/.claude/skills/github-workflow/SKILL.md
@@ -12,8 +12,11 @@ This skill provides standardized guidance for the complete GitHub development wo
 Follow this 10-step workflow for all feature development and bug fixes:
 
 ```
-Step 1: CREATE BRANCH
-  git checkout -b feat/<name> or fix/<name>
+Step 1: CREATE WORKTREE + BRANCH
+  Use git worktree for isolated development:
+    git worktree add .worktrees/<name> -b fix/<name>
+  Or for simple changes:
+    git checkout -b feat/<name> or fix/<name>
        ↓
 Step 2: IMPLEMENT CHANGES
   - Write code
@@ -77,6 +80,83 @@ Step 10: READY FOR MERGE (DO NOT MERGE)
   - User decides when to merge
 ```
 
+## Git Worktree Usage
+
+**Use git worktrees** to work on features, bug fixes, docs, or any git commits/PRs in an isolated workspace without affecting the current branch.
+
+### When to Use Worktrees
+
+| Scenario | Use Worktree? |
+|----------|---------------|
+| Bug fix while another branch has uncommitted work | **Yes** |
+| Feature development alongside existing work | **Yes** |
+| Parallel work on multiple PRs | **Yes** |
+| Quick single-file edit on current branch | No |
+| Docs-only change on current branch | No |
+
+### Step 1: Create Worktree
+
+```bash
+# Ensure .worktrees/ is in .gitignore (one-time setup)
+git check-ignore -q .worktrees || echo ".worktrees/" >> .gitignore
+
+# Create worktree with new branch from main
+git fetch origin main
+git worktree add .worktrees/<name> -b <branch-type>/<name> origin/main
+cd .worktrees/<name>
+
+# Install dependencies (worktrees don't share node_modules)
+npm install
+```
+
+Branch naming: `feat/<name>`, `fix/<name>`, `refactor/<name>`, `docs/<name>`
+
+### Step 2: Work in the Worktree
+
+```bash
+# All git operations happen in the worktree directory
+cd .worktrees/<name>
+
+# Build, test, commit as usual
+npm run build && npm run test
+git add <files> && git commit -m "type(scope): description"
+git push -u origin <branch-name>
+```
+
+**Important**: The shared `.venv/` (Python) lives in the main repo. Run Python tests with the full path:
+```bash
+/path/to/main-repo/.venv/bin/python -m pytest docker/test_*.py -v
+```
+
+### Step 3: Copy Local Files (if needed)
+
+Gitignored files (deploy scripts, local config) don't exist in worktrees:
+```bash
+cp /path/to/main-repo/deploy-staging.local.sh .worktrees/<name>/
+cp /path/to/main-repo/CLAUDE.local.md .worktrees/<name>/
+```
+
+### Step 4: Cleanup After Merge
+
+```bash
+# Remove worktree after PR is merged
+git worktree remove .worktrees/<name>
+
+# Or force-remove if there are uncommitted changes
+git worktree remove --force .worktrees/<name>
+
+# Delete the branch
+git branch -d <branch-type>/<name>
+```
+
+### Quick Reference
+
+```bash
+git worktree list                              # List all worktrees
+git worktree add .worktrees/foo -b fix/foo     # Create new worktree
+git worktree remove .worktrees/foo             # Remove worktree
+```
+
 ## E2E Test Selection
 
 Run `test/select-e2e-tests.sh` to automatically determine which tests to run based on changed files.
PATCH

echo "Gold patch applied."
