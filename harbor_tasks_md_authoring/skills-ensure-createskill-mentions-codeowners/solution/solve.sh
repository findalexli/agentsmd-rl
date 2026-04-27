#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "| Missing CODEOWNERS entry | Add entries for both `/plugins/<plugin>/skills/<ski" ".agents/skills/create-skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/create-skill/SKILL.md b/.agents/skills/create-skill/SKILL.md
@@ -78,7 +78,18 @@ skills/<skill-name>/
 └── assets/        # Templates, images, data files
 ```
 
-### Step 6: Validate the skill
+### Step 6: Update CODEOWNERS
+
+Add entries in `.github/CODEOWNERS` for the new skill and its test directory:
+
+```
+/plugins/<plugin>/skills/<skill-name>/  @owner-team
+/tests/<plugin>/<skill-name>/           @owner-team
+```
+
+Match the owner pattern used by sibling skills in the same plugin.
+
+### Step 7: Validate the skill
 
 - Confirm frontmatter fields are valid
 - Ensure SKILL.md is under 500 lines
@@ -149,6 +160,7 @@ After creating a skill, verify:
 - [ ] Workflow has numbered steps with clear checkpoints
 - [ ] Validation section exists with observable success criteria
 - [ ] No secrets, tokens, or internal URLs included
+- [ ] `.github/CODEOWNERS` has entries for the new skill and its test directory
 
 ## Common Pitfalls
 
@@ -160,6 +172,7 @@ After creating a skill, verify:
 | Missing validation steps | Add checkpoints that verify success |
 | SKILL.md too long | Move detailed content to `references/` files |
 | Hardcoded environment assumptions | Document requirements in `compatibility` field |
+| Missing CODEOWNERS entry | Add entries for both `/plugins/<plugin>/skills/<skill-name>/` and `/tests/<plugin>/<skill-name>/` matching sibling skills' owner pattern |
 
 ## References
 
PATCH

echo "Gold patch applied."
