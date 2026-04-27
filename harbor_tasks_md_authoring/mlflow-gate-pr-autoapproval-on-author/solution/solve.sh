#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotency guard
if grep -qF "- Otherwise (including API errors, e.g., 404 for non-collaborators) -> do NOT ap" ".claude/skills/pr-review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/pr-review/SKILL.md b/.claude/skills/pr-review/SKILL.md
@@ -74,8 +74,17 @@ For each issue found, use the `add-review-comment` skill to post review comments
 
 ### 6. Approve the PR
 
-Approve the PR when there are no issues or only minor issues.
+Approve the PR when there are no issues or only minor issues, but **only if the PR author has the `admin` or `maintain` role**.
+
+First, check the PR author's role:
 
 ```bash
-gh pr review <PR_NUMBER> --repo <owner/repo> --approve
+author=$(gh api repos/<owner>/<repo>/pulls/<PR_NUMBER> --jq '.user.login')
+gh api repos/<owner>/<repo>/collaborators/"$author"/permission --jq '.role_name'
 ```
+
+- If the role is `admin` or `maintain` -> approve the PR:
+  ```bash
+  gh pr review <PR_NUMBER> --repo <owner/repo> --approve
+  ```
+- Otherwise (including API errors, e.g., 404 for non-collaborators) -> do NOT approve. Do not mention the reason for not approving in the review.
PATCH

echo "Gold patch applied."
