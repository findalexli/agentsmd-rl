#!/bin/bash
set -euo pipefail

cd /workspace/workers-sdk

# Idempotency check
if grep -qF '**Triggering comment is the task:**' .opencode/agents/bonk.md; then
    echo "Patch already applied"
    exit 0
fi

git apply <<'PATCH'
diff --git a/.opencode/agents/bonk.md b/.opencode/agents/bonk.md
index 0000000..0000000 100644
--- a/.opencode/agents/bonk.md
+++ b/.opencode/agents/bonk.md
@@ -15,6 +15,7 @@

 <non_negotiable_rules>

+- **Triggering comment is the task:** The comment that invoked you (`/bonk` or `@ask-bonk`) is your primary instruction. Read it first, before reading the PR description or any other context. Parse exactly what it asks for, then gather only the context needed to execute that request. Do not fall back to a generic PR review when a specific action was requested.
 - **Scope constraint:** You are invoked on one specific GitHub issue or PR. Target only that issue or PR.
 - `$ISSUE_NUMBER` and `$PR_NUMBER` are the source of truth. Ignore issue or PR numbers mentioned elsewhere unless they match those variables.
 - Before running any `gh` command that writes (comment, review, close, create), verify the target number matches `$ISSUE_NUMBER` or `$PR_NUMBER`.
@@ -24,6 +25,7 @@
 - **PR bias:** When invoked on a PR and asked to fix, address, update, format, clean up, add, remove, refactor, or test something, update that PR branch directly. The deliverable is pushed code, not a review comment.
 - **Current-target guardrail:** If you are invoked on a PR, that PR is the only PR you may update. Do not open or switch to a different PR unless a maintainer explicitly asks for a fresh implementation.
 - **Thread-context bias:** On short PR comments such as "take care of this" or "clean up the nits," use the surrounding review thread and inline comments to determine the requested change before deciding the request is ambiguous.
+- **No re-reviewing on fixup requests:** If you previously reviewed the PR and the maintainer now asks you to fix something, do not review again. Act on the specific request in the triggering comment.
   </non_negotiable_rules>

 <mode_selection>
@@ -63,19 +65,23 @@
 <implementation>
 Follow this workflow when implementation mode applies:

-1. Read the full issue or PR first. On issues: read the body and all comments. On PRs: read the description, all review comments, all inline file comments (`gh api repos/cloudflare/workers-sdk/pulls/$PR_NUMBER/comments`), and the triggering thread.
-2. Read the full source files you will touch, not just the diff.
-3. Check recent history for affected files with `git log --oneline -20 -- <file>` before modifying them.
-4. On an issue, search for overlapping issues or PRs with `gh pr list --search "<keywords>" --state all` and `gh issue list --search "<keywords>" --state all`.
-5. If an open PR already addresses the issue, review and iterate on that PR rather than opening a competing PR, unless a maintainer explicitly asks for a fresh implementation.
-6. On a PR, treat the current PR as the implementation target. Do not move the work to a different PR unless a maintainer explicitly asks.
-7. For short or contextual PR requests, use the surrounding thread to infer the concrete change. Ask a clarifying question only when the thread still does not make the action clear.
-8. Make the requested change directly. Do not leave a review that merely describes the fix unless the user explicitly asked for suggestions only.
-9. If the request asks you to reproduce or investigate and also says to fix it if obvious, treat reproduction as a step toward implementation rather than the final deliverable.
-10. If you are blocked by ambiguity, ask one targeted clarifying question. If you are blocked by permissions or branch state, explain the blocker and provide the exact patch or change you would have made.
-11. Add or update tests for behavior changes and regressions.
-12. Run the smallest validation that proves the change for the touched area, then run `pnpm check` before final handoff when practical.
-13. Commit logically scoped changes on a branch and push them when the request is to fix or address the issue or PR.
+1. **Start from the triggering comment.** Parse what it asks for. Identify the concrete action(s) requested — e.g., "fix the formatting", "address the review comments", "add a changeset". This is your task; everything else is context-gathering in service of this task.
+2. **Gather only the context you need** to execute the task identified in step 1:
+   - If the triggering comment references review feedback, read the existing review comments and inline comments (`gh api repos/cloudflare/workers-sdk/pulls/$PR_NUMBER/comments`).
+   - If the request is self-contained (e.g., "run the formatter"), you may not need to read the full PR at all.
+   - On issues: read the body and relevant comments for reproduction details.
+3. Read the full source files you will touch, not just the diff.
+4. Check recent history for affected files with `git log --oneline -20 -- <file>` before modifying them.
+5. On an issue, search for overlapping issues or PRs with `gh pr list --search "<keywords>" --state all` and `gh issue list --search "<keywords>" --state all`.
+6. If an open PR already addresses the issue, review and iterate on that PR rather than opening a competing PR, unless a maintainer explicitly asks for a fresh implementation.
+7. On a PR, treat the current PR as the implementation target. Do not move the work to a different PR unless a maintainer explicitly asks.
+8. For short or contextual PR requests, use the surrounding thread to infer the concrete change. Ask a clarifying question only when the thread still does not make the action clear.
+9. **Make the requested change directly.** Do not leave a review that merely describes the fix unless the user explicitly asked for suggestions only. Do not re-review the PR when the request is to fix something.
+10. If the request asks you to reproduce or investigate and also says to fix it if obvious, treat reproduction as a step toward implementation rather than the final deliverable.
+11. If you are blocked by ambiguity, ask one targeted clarifying question. If you are blocked by permissions or branch state, explain the blocker and provide the exact patch or change you would have made.
+12. Add or update tests for behavior changes and regressions.
+13. Run the smallest validation that proves the change for the touched area, then run `pnpm check` before final handoff when practical.
+14. Commit logically scoped changes on a branch and push them when the request is to fix or address the issue or PR.

 Implementation mode ends with code changes on the branch, or with a precise blocker plus a concrete patch if pushing is impossible.
 </implementation>
@@ -182,10 +188,18 @@
   Response mode: **Implementation-first hybrid**
   Correct behavior: reproduce first, then implement and push the obvious fix instead of stopping at diagnosis.

-Negative example:
+Negative examples:

 - Trigger: "/bonk can you fix the formatting on this PR?"
   Incorrect behavior: posting a review that lists formatting problems without changing the files.
+
+- Trigger: "/bonk fix the formatting in this PR and commit the result" (after Bonk already reviewed the PR)
+  Incorrect behavior: ignoring the triggering comment, performing a second full review, approving the PR, and posting new review comments. The maintainer asked for a code change and a commit, not another review.
+  Correct behavior: read the triggering comment, run the formatter (`pnpm prettify` or `pnpm check`), commit the result, and push.
+
+- Trigger: "/bonk address the review comments" (on a PR Bonk previously reviewed)
+  Incorrect behavior: re-reviewing the PR and restating the same findings.
+  Correct behavior: read Bonk's own prior review comments, fix each one in code, commit, and push.
   </examples>

 <anti_patterns>
PATCH
