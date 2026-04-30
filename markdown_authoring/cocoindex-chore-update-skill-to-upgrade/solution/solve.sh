#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cocoindex

# Idempotency guard
if grep -qF "find examples -name \"pyproject.toml\" -not -path \"*/.venv/*\" -exec grep -l \"cocoi" ".claude/skills/upgrade-examples/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/upgrade-examples/SKILL.md b/.claude/skills/upgrade-examples/SKILL.md
@@ -17,20 +17,34 @@ Example: `/upgrade-examples 1.0.0a5`
 
 ## Instructions
 
-To upgrade all example dependencies:
+To upgrade all example dependencies (replace `VERSION` with the actual version, e.g., `1.0.0a10`):
 
-1. Parse the version from the user's argument (e.g., `1.0.0a5`)
+1. Create a new branch for the changes:
 
-2. Run the following command to update all example pyproject.toml files (replace `NEW_VERSION` with the actual version):
+```bash
+git checkout -b ex-dep-VERSION
+```
+
+2. Run the following command to update all example pyproject.toml files.
+
+**Important:** Use the literal version string directly in the sed command. Do not use shell variables as quoting issues can cause the version to be omitted.
 
 ```bash
-find examples -name "pyproject.toml" -not -path "*/.venv/*" -exec grep -l "cocoindex" {} \; | xargs sed -i '' 's/cocoindex\([^>]*\)>=[0-9][0-9a-zA-Z.]*/cocoindex\1>=NEW_VERSION/g'
+find examples -name "pyproject.toml" -not -path "*/.venv/*" -exec grep -l "cocoindex" {} \; | xargs sed -i '' 's/cocoindex\([^>]*\)>=[0-9][0-9a-zA-Z.]*/cocoindex\1>=VERSION/g'
 ```
 
-3. Verify the changes:
+3. Verify the changes show the correct version:
 
 ```bash
 grep -r "cocoindex.*>=" examples --include="pyproject.toml" | grep -v ".venv"
 ```
 
-4. Report the number of files updated and confirm all versions match the target.
+4. Commit and push the changes:
+
+```bash
+git add examples/*/pyproject.toml
+git commit -m "chore: upgrade examples deps to cocoindex-VERSION"
+git push -u origin ex-dep-VERSION
+```
+
+5. Report the number of files updated and provide the branch name for creating a PR.
PATCH

echo "Gold patch applied."
