#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vitess

# Idempotency guard
if grep -qF "- [ ] Golang code passes the `goimports -local \"vitess.io/vitess\" -w ...` format" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -259,7 +259,7 @@ func TestProcessor_ImprovedBehavior(t *testing.T) {
 - You may read git state: `git status`, `git log`, `git diff`, `git branch --show-current`
 - You may NOT: `git commit`, `git add`, `git reset`, `git checkout`, `git restore`, `git rebase`, `git push`, etc.
 - **ONLY commit when explicitly asked to commit**
-- Always sign git commits with the --signoff flag
+- Always sign git commits with the `git commit --signoff` flag
 - When asked to commit, do it once and stop
 - Only I can modify git state unless you've been given explicit permission to commit
 
@@ -334,7 +334,8 @@ Me: "Now let's optimize without breaking functionality"
 Before considering any work "done":
 - [ ] Tests pass and cover the feature
 - [ ] Code is clean and readable
-    - [ ] Code passes the `gofumpt` formatter
+    - [ ] Golang code passes the `gofumpt` formatter
+    - [ ] Golang code passes the `goimports -local "vitess.io/vitess" -w ...` formatter
 - [ ] Edge cases are handled
 - [ ] Performance is acceptable
 - [ ] Documentation is updated if needed
PATCH

echo "Gold patch applied."
