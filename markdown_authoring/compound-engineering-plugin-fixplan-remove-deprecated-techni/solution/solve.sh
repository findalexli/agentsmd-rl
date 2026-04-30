#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "6. **Start `/ce:work` on remote** - Begin implementing in Claude Code on the web" "plugins/compound-engineering/skills/ce-plan/SKILL.md" && grep -qF "3. **Deepen further** - Run another round of research on specific sections" "plugins/compound-engineering/skills/deepen-plan/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-plan/SKILL.md b/plugins/compound-engineering/skills/ce-plan/SKILL.md
@@ -579,17 +579,15 @@ After writing the plan file, use the **AskUserQuestion tool** to present these o
 **Options:**
 1. **Open plan in editor** - Open the plan file for review
 2. **Run `/deepen-plan`** - Enhance each section with parallel research agents (best practices, performance, UI)
-3. **Run `/technical_review`** - Technical feedback from code-focused reviewers (DHH, Kieran, Simplicity)
-4. **Review and refine** - Improve the document through structured self-review
-5. **Share to Proof** - Upload to Proof for collaborative review and sharing
-6. **Start `/ce:work`** - Begin implementing this plan locally
-7. **Start `/ce:work` on remote** - Begin implementing in Claude Code on the web (use `&` to run in background)
-8. **Create Issue** - Create issue in project tracker (GitHub/Linear)
+3. **Review and refine** - Improve the document through structured self-review
+4. **Share to Proof** - Upload to Proof for collaborative review and sharing
+5. **Start `/ce:work`** - Begin implementing this plan locally
+6. **Start `/ce:work` on remote** - Begin implementing in Claude Code on the web (use `&` to run in background)
+7. **Create Issue** - Create issue in project tracker (GitHub/Linear)
 
 Based on selection:
 - **Open plan in editor** → Run `open docs/plans/<plan_filename>.md` to open the file in the user's default editor
 - **`/deepen-plan`** → Call the /deepen-plan command with the plan file path to enhance with research
-- **`/technical_review`** → Call the /technical_review command with the plan file path
 - **Review and refine** → Load `document-review` skill.
 - **Share to Proof** → Upload the plan to Proof:
   ```bash
@@ -608,7 +606,7 @@ Based on selection:
 
 **Note:** If running `/ce:plan` with ultrathink enabled, automatically run `/deepen-plan` after plan creation for maximum depth and grounding.
 
-Loop back to options after Simplify or Other changes until user selects `/ce:work` or `/technical_review`.
+Loop back to options after Simplify or Other changes until user selects `/ce:work` or another action.
 
 ## Issue Creation
 
@@ -638,6 +636,6 @@ When user selects "Create Issue", detect their project tracker from CLAUDE.md:
 
 5. **After creation:**
    - Display the issue URL
-   - Ask if they want to proceed to `/ce:work` or `/technical_review`
+   - Ask if they want to proceed to `/ce:work`
 
 NEVER CODE! Just research and write the plan.
diff --git a/plugins/compound-engineering/skills/deepen-plan/SKILL.md b/plugins/compound-engineering/skills/deepen-plan/SKILL.md
@@ -480,14 +480,12 @@ After writing the enhanced plan, use the **AskUserQuestion tool** to present the
 
 **Options:**
 1. **View diff** - Show what was added/changed
-2. **Run `/technical_review`** - Get feedback from reviewers on enhanced plan
-3. **Start `/ce:work`** - Begin implementing this enhanced plan
-4. **Deepen further** - Run another round of research on specific sections
-5. **Revert** - Restore original plan (if backup exists)
+2. **Start `/ce:work`** - Begin implementing this enhanced plan
+3. **Deepen further** - Run another round of research on specific sections
+4. **Revert** - Restore original plan (if backup exists)
 
 Based on selection:
 - **View diff** → Run `git diff [plan_path]` or show before/after
-- **`/technical_review`** → Call the /technical_review command with the plan file path
 - **`/ce:work`** → Call the /ce:work command with the plan file path
 - **Deepen further** → Ask which sections need more research, then re-run those agents
 - **Revert** → Restore from git or backup
PATCH

echo "Gold patch applied."
