#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fastled

# Idempotency guard
if grep -qF "- **Default mindset: finish the job.** Agents should not leave uncommitted chang" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -40,9 +40,19 @@ See `agents/docs/build-system.md` for full command execution rules and forbidden
 ## Core Rules (ALL AGENTS)
 
 ### Git and Code Publishing
-- **Committing and pushing to feature branches is allowed** — including pushing a branch or PR for testing and merge
-- **NEVER commit or push directly to `master`/`main`** — always use a feature branch
-- **NEVER force-push** to shared branches (master/main, or any branch with an open PR others may be reviewing)
+- **Default mindset: finish the job.** Agents should not leave uncommitted changes dangling on `master`/`main`. If you made edits on `master`, the correct end-state is a feature branch + pushed PR — not a dirty working tree.
+- **Feature branches — full autonomy, no user consent required.** Agents may freely create branches, commit, push, and open PRs against any branch that is NOT `master`/`main`. Do this proactively when work is complete.
+- **`master`/`main` — extra caution required.**
+  - NEVER commit directly to `master`/`main`.
+  - NEVER push directly to `master`/`main`.
+  - NEVER force-push to `master`/`main` (or any branch with an open PR others may be reviewing).
+  - If changes exist on `master`, move them: `git checkout -b feat/<topic>` carries the working-tree changes to a feature branch, then commit + push + open a PR there.
+- **Recovery pattern for uncommitted changes on `master`:**
+  1. `git status` — confirm scope
+  2. `git checkout -b <descriptive-branch>` — changes follow to new branch
+  3. `git add <specific files>` + `git commit` (conventional commit format)
+  4. `git push -u origin <branch>` and `gh pr create`
+  5. `git status` again to confirm clean tree
 
 ### Hook Error Policy
 - **ALWAYS stop and fix Write/Edit hook errors immediately** before writing the next file
PATCH

echo "Gold patch applied."
