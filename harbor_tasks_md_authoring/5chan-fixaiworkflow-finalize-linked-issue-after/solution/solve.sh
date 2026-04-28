#!/usr/bin/env bash
set -euo pipefail

cd /workspace/5chan

# Idempotency guard
if grep -qF "description: Review an open GitHub pull request, inspect feedback from Cursor Bu" ".codex/skills/review-and-merge-pr/SKILL.md" && grep -qF "description: Review an open GitHub pull request, inspect feedback from Cursor Bu" ".cursor/skills/review-and-merge-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.codex/skills/review-and-merge-pr/SKILL.md b/.codex/skills/review-and-merge-pr/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: review-and-merge-pr
-description: Review an open GitHub pull request, inspect feedback from Cursor Bugbot, CodeRabbit, CI, and human reviewers, decide which findings are valid, implement fixes on the PR branch, and merge the PR into master when it is ready. Use when the user says "check the PR", "address bugbot comments", "handle CodeRabbit feedback", "review PR feedback", or "merge this PR".
+description: Review an open GitHub pull request, inspect feedback from Cursor Bugbot, CodeRabbit, CI, and human reviewers, decide which findings are valid, implement fixes on the PR branch, merge the PR into master when it is ready, and finalize the linked GitHub issue and project status after merge. Use when the user says "check the PR", "address bugbot comments", "handle CodeRabbit feedback", "review PR feedback", or "merge this PR".
 ---
 
 # Review And Merge Pr
@@ -113,7 +113,38 @@ Preferred merge command:
 gh pr merge <pr-number> --repo bitsocialnet/5chan --squash --delete-branch
 ```
 
-### 7. Clean up local state after merge
+### 7. Finalize the linked issue and project item
+
+After merge, inspect the PR's linked closing issue.
+If the merge did not close the issue automatically, close it manually.
+Then ensure the linked issue is on the `5chan` project and its status is `Done`.
+
+Useful commands:
+
+```bash
+ISSUE_NUMBER=$(gh pr view <pr-number> --repo bitsocialnet/5chan --json closingIssuesReferences --jq '.closingIssuesReferences[0].number // empty')
+
+if [ -n "$ISSUE_NUMBER" ]; then
+  ISSUE_STATE=$(gh issue view "$ISSUE_NUMBER" --repo bitsocialnet/5chan --json state --jq '.state')
+  if [ "$ISSUE_STATE" != "CLOSED" ]; then
+    gh issue close "$ISSUE_NUMBER" --repo bitsocialnet/5chan
+  fi
+
+  ITEM_ID=$(gh project item-list 1 --owner bitsocialnet --format json --jq ".items[] | select(.content.number == $ISSUE_NUMBER) | .id" | head -n1)
+  if [ -z "$ITEM_ID" ]; then
+    ITEM_JSON=$(gh project item-add 1 --owner bitsocialnet --url "https://github.com/bitsocialnet/5chan/issues/$ISSUE_NUMBER" --format json)
+    ITEM_ID=$(echo "$ITEM_JSON" | jq -r '.id')
+  fi
+
+  FIELD_JSON=$(gh project field-list 1 --owner bitsocialnet --format json)
+  STATUS_FIELD_ID=$(echo "$FIELD_JSON" | jq -r '.fields[] | select(.name=="Status") | .id')
+  DONE_OPTION_ID=$(echo "$FIELD_JSON" | jq -r '.fields[] | select(.name=="Status") | .options[] | select(.name=="Done") | .id')
+
+  gh project item-edit --id "$ITEM_ID" --project-id PVT_kwDODohK7M4BM4wg --field-id "$STATUS_FIELD_ID" --single-select-option-id "$DONE_OPTION_ID"
+fi
+```
+
+### 8. Clean up local state after merge
 
 After the PR is merged:
 
@@ -130,12 +161,14 @@ git worktree list
 git worktree remove /path/to/worktree
 ```
 
-### 8. Report the outcome
+### 9. Report the outcome
 
 Tell the user:
 
 - which findings were fixed
 - which findings were declined and why
 - which verification commands ran
 - whether the PR was merged
+- whether the linked issue was confirmed closed
+- whether the linked project item was confirmed `Done`
 - whether the branch and any worktree were cleaned up
diff --git a/.cursor/skills/review-and-merge-pr/SKILL.md b/.cursor/skills/review-and-merge-pr/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: review-and-merge-pr
-description: Review an open GitHub pull request, inspect feedback from Cursor Bugbot, CodeRabbit, CI, and human reviewers, decide which findings are valid, implement fixes on the PR branch, and merge the PR into master when it is ready. Use when the user says "check the PR", "address bugbot comments", "handle CodeRabbit feedback", "review PR feedback", or "merge this PR".
+description: Review an open GitHub pull request, inspect feedback from Cursor Bugbot, CodeRabbit, CI, and human reviewers, decide which findings are valid, implement fixes on the PR branch, merge the PR into master when it is ready, and finalize the linked GitHub issue and project status after merge. Use when the user says "check the PR", "address bugbot comments", "handle CodeRabbit feedback", "review PR feedback", or "merge this PR".
 ---
 
 # Review And Merge Pr
@@ -113,7 +113,38 @@ Preferred merge command:
 gh pr merge <pr-number> --repo bitsocialnet/5chan --squash --delete-branch
 ```
 
-### 7. Clean up local state after merge
+### 7. Finalize the linked issue and project item
+
+After merge, inspect the PR's linked closing issue.
+If the merge did not close the issue automatically, close it manually.
+Then ensure the linked issue is on the `5chan` project and its status is `Done`.
+
+Useful commands:
+
+```bash
+ISSUE_NUMBER=$(gh pr view <pr-number> --repo bitsocialnet/5chan --json closingIssuesReferences --jq '.closingIssuesReferences[0].number // empty')
+
+if [ -n "$ISSUE_NUMBER" ]; then
+  ISSUE_STATE=$(gh issue view "$ISSUE_NUMBER" --repo bitsocialnet/5chan --json state --jq '.state')
+  if [ "$ISSUE_STATE" != "CLOSED" ]; then
+    gh issue close "$ISSUE_NUMBER" --repo bitsocialnet/5chan
+  fi
+
+  ITEM_ID=$(gh project item-list 1 --owner bitsocialnet --format json --jq ".items[] | select(.content.number == $ISSUE_NUMBER) | .id" | head -n1)
+  if [ -z "$ITEM_ID" ]; then
+    ITEM_JSON=$(gh project item-add 1 --owner bitsocialnet --url "https://github.com/bitsocialnet/5chan/issues/$ISSUE_NUMBER" --format json)
+    ITEM_ID=$(echo "$ITEM_JSON" | jq -r '.id')
+  fi
+
+  FIELD_JSON=$(gh project field-list 1 --owner bitsocialnet --format json)
+  STATUS_FIELD_ID=$(echo "$FIELD_JSON" | jq -r '.fields[] | select(.name=="Status") | .id')
+  DONE_OPTION_ID=$(echo "$FIELD_JSON" | jq -r '.fields[] | select(.name=="Status") | .options[] | select(.name=="Done") | .id')
+
+  gh project item-edit --id "$ITEM_ID" --project-id PVT_kwDODohK7M4BM4wg --field-id "$STATUS_FIELD_ID" --single-select-option-id "$DONE_OPTION_ID"
+fi
+```
+
+### 8. Clean up local state after merge
 
 After the PR is merged:
 
@@ -130,12 +161,14 @@ git worktree list
 git worktree remove /path/to/worktree
 ```
 
-### 8. Report the outcome
+### 9. Report the outcome
 
 Tell the user:
 
 - which findings were fixed
 - which findings were declined and why
 - which verification commands ran
 - whether the PR was merged
+- whether the linked issue was confirmed closed
+- whether the linked project item was confirmed `Done`
 - whether the branch and any worktree were cleaned up
PATCH

echo "Gold patch applied."
