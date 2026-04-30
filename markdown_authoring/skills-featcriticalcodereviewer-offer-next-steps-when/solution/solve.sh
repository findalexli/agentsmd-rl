#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "- Submit your review verbatim as a PR comment with attribution at the top: \"Revi" "posit-dev/critical-code-reviewer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/posit-dev/critical-code-reviewer/SKILL.md b/posit-dev/critical-code-reviewer/SKILL.md
@@ -148,6 +148,23 @@ Ask yourself:
 
 If you can't answer the first three, you haven't reviewed deeply enough.
 
+## Next Steps
+
+At the end of the review, suggest next steps that the user can take:
+
+1. Discuss and address review questions
+   - If the user chooses this option, use the AskUserQuestion tool to systematically talk through each of the issues identified in your review.
+   - Ask questions in groups by related severity or topic
+   - Offer resolution options and clearly mark your recommended choice
+
+2. Add your feedback to a pull request
+   - Offer this next step when the review is attached to a pull request
+   - Submit your review verbatim as a PR comment with attribution at the top: "Review feedback assisted by the [critical-code-reviewer skill](https://github.com/posit-dev/skills/blob/main/posit-dev/critical-code-reviewer/SKILL.md)."
+
+You can offer additional next step options based on the context of your conversation.
+
+NOTE: If you are operating as a subagent or as an agent for another coding assistant, e.g. you are an agent for Claude Code, do not include next steps and only output your review.
+
 ## Response Format
 
 ```
@@ -165,6 +182,9 @@ If you can't answer the first three, you haven't reviewed deeply enough.
 
 ## Verdict
 Request Changes | Needs Discussion | Approve
+
+## Next Steps
+[Numbered options for proceeding, e.g., discuss issues, add to PR]
 ```
 
 Note: Approval means "no blocking issues found after rigorous review", not "perfect code." Don't manufacture problems to avoid approving.
PATCH

echo "Gold patch applied."
