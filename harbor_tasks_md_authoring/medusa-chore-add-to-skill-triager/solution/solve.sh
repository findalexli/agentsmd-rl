#!/usr/bin/env bash
set -euo pipefail

cd /workspace/medusa

# Idempotency guard
if grep -qF "- [ ] Approving a PR that changes behavior documented as intentional \u2014 always ch" ".claude/skills/reviewing-prs/SKILL.md" && grep -qF "- **Is the behavior being changed intentional and documented?** If the PR modifi" ".claude/skills/reviewing-prs/reference/comment-guidelines.md" && grep -qF "- [ ] Confirming a bug without first checking the documentation \u2014 always check i" ".claude/skills/triaging-issues/SKILL.md" && grep -qF "> **CRITICAL:** Before treating anything as a bug, check the official Medusa doc" ".claude/skills/triaging-issues/reference/bug-report.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/reviewing-prs/SKILL.md b/.claude/skills/reviewing-prs/SKILL.md
@@ -309,6 +309,7 @@ bash scripts/labels.sh <pr_number> remove initial-approval
 
 - [ ] Checking template compliance for team members — skip for team members
 - [ ] Being vague about required changes — always list exactly what needs to change and why
+- [ ] Approving a PR that changes behavior documented as intentional — always check the docs when a PR modifies existing behavior; if the docs describe it as by design, flag it as `requires-more`
 - [ ] Closing a PR without a clear explanation
 - [ ] Forgetting the docs-ui test requirement for `www/packages/docs-ui/` changes
 - [ ] Skipping the integration test check for API route changes in `packages/medusa/src/api/`
diff --git a/.claude/skills/reviewing-prs/reference/comment-guidelines.md b/.claude/skills/reviewing-prs/reference/comment-guidelines.md
@@ -84,6 +84,7 @@ Before composing the review, assess whether the changes make sense in the broade
 
 **Ask yourself:**
 
+- **Is the behavior being changed intentional and documented?** If the PR modifies existing behavior, check whether that behavior is described as by design in the official Medusa documentation (`www/apps/book/app/learn/`). If the docs explicitly describe the current behavior as intentional, the PR is changing intended behavior and must be flagged as `requires-more`. Explain that the behavior is by design and reference the documentation section. This is a **blocking** concern — do not apply `initial-approval`.
 - **Does it make sense?** Does the implementation actually solve the problem described in the PR or linked issue? Is the approach reasonable, or is there a simpler/safer way?
 - **Are there unintended side effects?** Could the change break or alter behaviour in other areas of the codebase? For example: shared utilities, middleware, event handlers, or widely-used types.
 - **Is the scope right?** Does the PR do more or less than what the linked issue asks for? Extra unrelated changes are a flag.
diff --git a/.claude/skills/triaging-issues/SKILL.md b/.claude/skills/triaging-issues/SKILL.md
@@ -178,6 +178,7 @@ Whenever linking to Medusa docs in a comment, load `reference/doc-links.md` to c
 
 - [ ] Triaging a comment that is just an ongoing user conversation — exit early instead
 - [ ] Categorizing based on comments instead of the original issue body
+- [ ] Confirming a bug without first checking the documentation — always check if the behavior is documented as intentional before treating it as a bug
 - [ ] Closing an issue without leaving a comment explaining why
 - [ ] Adding `good-first-issue` or `help-wanted` before confirming the bug in the codebase
 - [ ] Skipping the docs/codebase check for feature requests
diff --git a/.claude/skills/triaging-issues/reference/bug-report.md b/.claude/skills/triaging-issues/reference/bug-report.md
@@ -31,9 +31,45 @@ Once we have this information, we'll look into it further.
 
 ---
 
-## Step 2 — Check for User Error
+## Step 2 — Check Documentation for Intentional Behavior
 
-Before validating the bug in code, assess whether the issue may be caused by the user:
+> **CRITICAL:** Before treating anything as a bug, check the official Medusa documentation to determine if the reported behavior is **intentional and documented**. Do this actively — search the docs and the codebase for explanations of the feature.
+
+Read the relevant documentation section (e.g. `www/apps/book/app/learn/fundamentals/`) for the feature mentioned in the issue. Ask: "Is the behavior the user is reporting described as by design anywhere in the docs?"
+
+**If the behavior is explicitly documented as by design:**
+1. Add a comment explaining the behavior is intentional, referencing the relevant documentation section
+2. Close the issue
+3. **Stop** — this is not a bug
+
+**Comment template — documented intentional behavior:**
+```
+Thank you for the report! After investigating, the behavior you're describing is actually intentional and documented.
+
+[Explain the behavior and why it works this way]
+
+You can find more details in our [documentation](link-to-relevant-docs-section).
+
+If you'd like a different behavior, we'd suggest [workaround or alternative approach if applicable].
+
+I'm going to close this issue, but feel free to reopen if your situation differs from what I've described.
+```
+
+Then: `bash scripts/close_issue.sh <issue_number>`
+
+---
+
+**If the behavior is undocumented or the docs are unclear/misleading** (but it still turns out to be by design after codebase review), treat it as a documentation gap — see Step 3 below.
+
+---
+
+**If the behavior is NOT described in the docs at all**, continue to Step 2.5.
+
+---
+
+## Step 2.5 — Check for User Error
+
+After verifying it's not documented intentional behavior, assess whether the issue may be caused by the user:
 
 - Incorrect usage not matching the [Medusa docs](https://docs.medusajs.com)
 - Custom code that diverges from documented patterns
PATCH

echo "Gold patch applied."
