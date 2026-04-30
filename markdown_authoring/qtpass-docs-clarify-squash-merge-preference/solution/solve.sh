#!/usr/bin/env bash
set -euo pipefail

cd /workspace/qtpass

# Idempotency guard
if grep -qF "**Avoid force pushing to shared branches** - Only force push to feature branches" ".opencode/skills/qtpass-github/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.opencode/skills/qtpass-github/SKILL.md b/.opencode/skills/qtpass-github/SKILL.md
@@ -84,14 +84,38 @@ git push -u origin new-branch-name
 
 ## Merging PRs
 
+**Preferred: Squash merge for long PR threads**
+
+Squash merging keeps the main branch history clean and avoids cluttering it with numerous intermediate commits from review iterations.
+
 ```bash
-# Merge via GitHub CLI (if you have admin rights)
-gh pr merge <PR_NUMBER> --admin --merge
+# Squash merge via GitHub CLI
+gh pr merge <PR_NUMBER> --squash --auto --delete-branch --subject "fix: description"
 
-# Or squash merge
+# Or with auto-merge (waits for CI)
 gh pr merge <PR_NUMBER> --squash --auto --delete-branch
 ```
 
+**Avoid force pushing to shared branches** - Only force push to feature branches when absolutely necessary (e.g., resolving merge conflicts, cleaning up commits). Never force push to main or branches that others may be working from.
+
+**Merge strategies:**
+
+| Strategy | Use Case                                             |
+| -------- | ---------------------------------------------------- |
+| Squash   | Feature PRs with multiple review commits (preferred) |
+| Merge    | PRs where individual commits have meaningful history |
+| Rebase   | Clean, linear history (rarely used here)             |
+
+**When to use merge (not squash):**
+
+- Hotfixes that need individual commits for rollback
+- PRs with distinct, logically separate changes
+
+```bash
+# Regular merge (when needed)
+gh pr merge <PR_NUMBER> --merge --auto --delete-branch
+```
+
 ## Commenting on Issues/PRs
 
 ```bash
PATCH

echo "Gold patch applied."
