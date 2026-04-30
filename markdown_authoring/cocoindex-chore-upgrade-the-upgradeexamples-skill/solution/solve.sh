#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cocoindex

# Idempotency guard
if grep -qF "6. Report the number of files updated and provide the PR link from the `gh pr cr" ".claude/skills/upgrade-examples/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/upgrade-examples/SKILL.md b/.claude/skills/upgrade-examples/SKILL.md
@@ -47,4 +47,10 @@ git commit -m "chore: upgrade examples deps to cocoindex-VERSION"
 git push -u origin ex-dep-VERSION
 ```
 
-5. Report the number of files updated and provide the branch name for creating a PR.
+5. Create a PR using the `gh` CLI and capture the PR URL from its output:
+
+```bash
+gh pr create --base v1 --title "chore: upgrade examples deps to cocoindex-VERSION" --body ""
+```
+
+6. Report the number of files updated and provide the PR link from the `gh pr create` output to the user.
PATCH

echo "Gold patch applied."
