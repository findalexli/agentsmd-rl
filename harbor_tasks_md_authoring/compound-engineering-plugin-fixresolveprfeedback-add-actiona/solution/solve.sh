#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "1. **Actionability**: Skip items that contain no actionable feedback or question" "plugins/compound-engineering/skills/resolve-pr-feedback/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/resolve-pr-feedback/SKILL.md b/plugins/compound-engineering/skills/resolve-pr-feedback/SKILL.md
@@ -60,9 +60,12 @@ Before processing, classify each piece of feedback as **new** or **already handl
 
 **Review threads**: Read the thread's comments. If there's a substantive reply that acknowledges the concern but defers action (e.g., "need to align on this", "going to think through this", or a reply that presents options without resolving), it's a **pending decision** -- don't re-process. If there's only the original reviewer comment(s) with no substantive response, it's **new**.
 
-**PR comments and review bodies**: These have no resolve mechanism, so they reappear on every run. Check the PR conversation for an existing reply that quotes and addresses the feedback. If a reply already exists, skip. If not, it's new.
+**PR comments and review bodies**: These have no resolve mechanism, so they reappear on every run. Apply two filters in order:
 
-The distinction is about content, not who posted what. A deferral from a teammate, a previous skill run, or a manual reply all count.
+1. **Actionability**: Skip items that contain no actionable feedback or questions to answer. Examples: review wrapper text ("Here are some automated review suggestions..."), approvals ("this looks great!"), status badges ("Validated"), CI summaries with no follow-up asks. If there's nothing to fix, answer, or decide, it's not actionable -- drop it from the count entirely.
+2. **Already replied**: For actionable items, check the PR conversation for an existing reply that quotes and addresses the feedback. If a reply already exists, skip. If not, it's new.
+
+The distinction is about content, not who posted what. A deferral from a teammate, a previous skill run, or a manual reply all count. Similarly, actionability is about content -- bot feedback that requests a specific code change is actionable; a bot's boilerplate header wrapping those requests is not.
 
 If there are no new items across all feedback types, skip steps 3-8 and go straight to step 9.
 
@@ -74,10 +77,10 @@ Before planning and dispatching fixes, check whether feedback patterns suggest a
 
 | Gate signal | Check |
 |---|---|
-| **Volume** | 4+ new items from triage |
+| **Volume** | 3+ new items from triage |
 | **Verify-loop re-entry** | This is the 2nd+ pass through the workflow (new feedback appeared after a previous fix round) |
 
-If the gate does not fire, proceed to step 4. The common case (1-3 unrelated comments) skips this step entirely with zero overhead.
+If the gate does not fire, proceed to step 4. The common case (1-2 unrelated comments) skips this step entirely with zero overhead.
 
 **If the gate fires**, analyze feedback for thematic clusters:
 
PATCH

echo "Gold patch applied."
