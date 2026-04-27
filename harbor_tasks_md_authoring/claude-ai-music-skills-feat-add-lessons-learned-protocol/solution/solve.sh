#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-ai-music-skills

# Idempotency guard
if grep -qF "**When you discover a technical issue during production** (pronunciation error, " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -314,6 +314,38 @@ See `/skills/resume/SKILL.md` for full documentation.
 
 **The rule**: Changes to workflow files take effect immediately. Re-read the relevant section after any edit to ensure you're following the updated process.
 
+## Lessons Learned Protocol
+
+**When you discover a technical issue during production** (pronunciation error, rhyme violation, formatting problem, wrong assumption), don't just fix it — propose a rule to prevent it from happening again.
+
+### Process
+
+1. **Fix the immediate issue** in the current track/file
+2. **Sweep the album** for the same issue in other tracks
+3. **Draft a rule** — specific, actionable, with examples
+4. **Present to user**: "I found [issue]. Here's a rule to prevent this: [rule]. Should I add it to [location]?"
+5. **Log the lesson** — add the rule to the appropriate file (SKILL.md, CLAUDE.md, genre README, or reference doc)
+
+### What Qualifies
+
+- Pronunciation errors Suno got wrong (add to pronunciation guide)
+- Rhyme pattern violations that slipped through review
+- Formatting issues that caused generation problems
+- Assumptions that turned out wrong for a genre/style
+- Manual corrections that should be automated checks
+
+### Rule Format
+
+When proposing a rule, include:
+- **What went wrong**: The specific issue encountered
+- **Why it matters**: Impact on output quality
+- **The rule**: Clear, actionable instruction
+- **Examples**: Before/after showing the fix
+
+### Key Principle
+
+**Be proactive.** When you correct something manually, ask yourself: "Should this be a rule?" If the answer is yes, propose it immediately. Don't wait to be asked.
+
 ---
 
 ## Core Principles
PATCH

echo "Gold patch applied."
