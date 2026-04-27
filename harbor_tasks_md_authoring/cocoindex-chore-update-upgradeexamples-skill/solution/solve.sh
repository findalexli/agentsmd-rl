#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cocoindex

# Idempotency guard
if grep -qF "7. Report the number of files updated and provide the PR link from the `gh pr cr" ".claude/skills/upgrade-examples/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/upgrade-examples/SKILL.md b/.claude/skills/upgrade-examples/SKILL.md
@@ -53,4 +53,11 @@ git push -u origin ex-dep-VERSION
 gh pr create --base v1 --title "chore: upgrade examples deps to cocoindex-VERSION" --body ""
 ```
 
-6. Report the number of files updated and provide the PR link from the `gh pr create` output to the user.
+6. Switch back to the previous branch and delete the local branch:
+
+```bash
+git checkout v1
+git branch -d ex-dep-VERSION
+```
+
+7. Report the number of files updated and provide the PR link from the `gh pr create` output to the user.
PATCH

echo "Gold patch applied."
