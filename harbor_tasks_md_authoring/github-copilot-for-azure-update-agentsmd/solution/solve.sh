#!/usr/bin/env bash
set -euo pipefail

cd /workspace/github-copilot-for-azure

# Idempotency guard
if grep -qF "> **For AI Agents**: Do not add or change files outside of the new test director" "tests/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/tests/AGENTS.md b/tests/AGENTS.md
@@ -11,6 +11,8 @@ When a user asks to scaffold, create, or add tests for a skill, follow these ste
 cp -r tests/_template tests/{skill-name}
 ```
 
+> **For AI Agents**: Do not add or change files outside of the new test directory.
+
 ### Step 2: Read the skill's SKILL.md
 Load the file at `plugin/skills/{skill-name}/SKILL.md` to understand:
 - The skill's name and description (from frontmatter)
PATCH

echo "Gold patch applied."
