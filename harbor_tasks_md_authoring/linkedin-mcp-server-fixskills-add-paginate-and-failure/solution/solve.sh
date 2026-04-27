#!/usr/bin/env bash
set -euo pipefail

cd /workspace/linkedin-mcp-server

# Idempotency guard
if grep -qF "- If a failure cannot be fixed automatically, skip that fix and report it as **V" ".agents/skills/triage-reviews/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/triage-reviews/SKILL.md b/.agents/skills/triage-reviews/SKILL.md
@@ -17,9 +17,9 @@ Fetch all review comments on the current PR, verify each finding against real co
 
 2. Fetch ALL comments (reviewers post in multiple places):
    ```
-   gh api repos/{owner}/{repo}/pulls/{pr}/reviews
-   gh api repos/{owner}/{repo}/pulls/{pr}/comments
-   gh api repos/{owner}/{repo}/issues/{pr}/comments
+   gh api --paginate repos/{owner}/{repo}/pulls/{pr}/reviews
+   gh api --paginate repos/{owner}/{repo}/pulls/{pr}/comments
+   gh api --paginate repos/{owner}/{repo}/issues/{pr}/comments
    ```
 
 3. Extract unique findings — deduplicate across Copilot, Greptile, and human reviewers. Group by file and line.
@@ -32,7 +32,7 @@ For EVERY finding, verify against real code before accepting or rejecting:
 2. **Check if the issue still exists** — it may already be fixed in a later commit
 3. **Verify correctness** using:
    - Code analysis (read surrounding context, trace call paths)
-   - `btca ask -r <resource> -q "..."` for library/framework questions
+   - `btca ask -r <resource> -q "..."` for library/framework questions (`btca resources` to list available)
    - Web search for API behavior, language semantics, or CVEs
 4. **Classify** each finding:
    - **Valid** — real bug, real gap, or real improvement needed
@@ -42,6 +42,8 @@ For EVERY finding, verify against real code before accepting or rejecting:
 
 1. Fix all **Valid** findings
 2. Run the project's lint/test commands (check CLAUDE.md for exact commands)
+   - If lint/tests fail, fix the failures before committing
+   - If a failure cannot be fixed automatically, skip that fix and report it as **Valid (unfixed)** in the Phase 4 table
 3. `git add` only changed files, `git commit` with message:
    ```
    fix: Address PR review feedback
PATCH

echo "Gold patch applied."
