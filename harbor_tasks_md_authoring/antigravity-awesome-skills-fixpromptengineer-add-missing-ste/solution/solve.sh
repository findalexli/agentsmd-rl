#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "**Critical Rule:** When in doubt, skip clarification and generate the best promp" "skills/prompt-engineer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/prompt-engineer/SKILL.md b/skills/prompt-engineer/SKILL.md
@@ -53,6 +53,34 @@ Invoke this skill when:
 - **Structured tasks:** Mentions steps, phases, deliverables, stakeholders
 
 
+### Step 2: Ask Clarifying Questions (Conditional)
+
+**Objective:** Gather missing information only when it is critical to framework selection or prompt quality.
+
+**Trigger Conditions** — ask only if:
+- Task type is completely ambiguous (cannot determine coding vs. writing vs. analysis)
+- Target audience is unknown and materially affects the output
+- Scope is undefined and choosing wrong scope would invalidate the prompt
+- Requested output format conflicts or is missing and cannot be inferred
+
+**Question Limits:**
+- Maximum 3 questions per invocation
+- Combine related questions into one when possible
+- If enough context exists, skip this step entirely (most cases)
+
+**Example Clarifying Exchange:**
+
+```
+User: "help me with AI"
+
+Step 2 (triggered — task type ambiguous):
+"To craft the best prompt, I need one quick clarification:
+1. What do you want to do with AI — build something, learn about it, or use an AI tool for a task?"
+```
+
+**Critical Rule:** When in doubt, skip clarification and generate the best prompt with available context. Over-asking breaks the "magic mode" experience.
+
+
 ### Step 3: Select Framework(s)
 
 **Objective:** Map task characteristics to optimal prompting framework(s).
PATCH

echo "Gold patch applied."
