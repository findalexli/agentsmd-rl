#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "Offer these two options. Use the document type from Phase 1 to set the \"Review c" "plugins/compound-engineering/skills/document-review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/document-review/SKILL.md b/plugins/compound-engineering/skills/document-review/SKILL.md
@@ -26,6 +26,7 @@ Callers invoke headless mode by including `mode:headless` in the skill arguments
 Skill("compound-engineering:document-review", "mode:headless docs/plans/my-plan.md")
 ```
 
+
 If `mode:headless` is not present, the skill runs in its default interactive mode with no behavior change.
 
 ## Phase 1: Get and Analyze Document
@@ -254,10 +255,12 @@ These are pipeline artifacts and must not be flagged for removal.
 - Gemini: `ask_user`
 - Fallback (no question tool available): present numbered options and stop; wait for the user's next message
 
-Offer:
+Offer these two options. Use the document type from Phase 1 to set the "Review complete" description:
 
-1. **Refine again** -- another review pass
-2. **Review complete** -- document is ready
+1. **Refine again** -- Address the findings above, then re-review
+2. **Review complete** -- description based on document type:
+   - requirements document: "Create technical plan with ce:plan"
+   - plan document: "Implement with ce:work"
 
 After 2 refinement passes, recommend completion -- diminishing returns are likely. But if the user wants to continue, allow it.
 
PATCH

echo "Gold patch applied."
