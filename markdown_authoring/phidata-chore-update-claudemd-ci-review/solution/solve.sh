#!/usr/bin/env bash
set -euo pipefail

cd /workspace/phidata

# Idempotency guard
if grep -qF "Every non-draft PR automatically receives a review from Opus using both `code-re" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -244,8 +244,12 @@ gh api repos/agno-agi/agno/pulls/<PR_NUMBER> -X PATCH -f body="$(cat /path/to/bo
 
 ## CI: Automated Code Review
 
-Every non-draft PR automatically receives a deep review from Opus using `/review-pr` stacked with the `pr-review-toolkit` plugin (6 specialized agents). No manual trigger needed.
+Every non-draft PR automatically receives a review from Opus using both `code-review` and `pr-review-toolkit` official plugins (10 specialized agents total). No manual trigger needed — the review posts as a sticky comment on the PR.
 
-When running in GitHub Actions (CI) and a user mentions `@claude` asking for a review, use `/review-pr` to run a fresh review pass.
+When running in GitHub Actions (CI), always end your response with a plain-text summary of findings. Never let the final action be a tool call. If there are no issues, say "No high-confidence findings."
 
-**CI output rule:** When running as a CI reviewer, always end your response with a plain-text summary of findings. Never let the final action be a tool call — the GitHub Action uses the text output to post the sticky PR comment. If there are no issues, say so explicitly.
+Agno-specific checks to always verify:
+- Both sync and async variants exist for all new public methods
+- No agent creation inside loops (agents should be reused)
+- CLAUDE.md coding patterns are followed
+- No f-strings for print lines where there are no variables
PATCH

echo "Gold patch applied."
