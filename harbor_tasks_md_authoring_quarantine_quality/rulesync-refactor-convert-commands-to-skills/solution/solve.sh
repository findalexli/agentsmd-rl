#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rulesync

# Idempotency guard
if grep -qF "name: clean-worktrees" ".rulesync/skills/clean-worktrees/SKILL.md" && grep -qF "name: create-issue" ".rulesync/skills/create-issue/SKILL.md" && grep -qF "description: \"Explain a PR: the background problem and the proposed solution\"" ".rulesync/skills/explain-pr/SKILL.md" && grep -qF "description: Merge a pull request using gh pr merge --admin" ".rulesync/skills/merge-pr/SKILL.md" && grep -qF "name: post-review-comment" ".rulesync/skills/post-review-comment/SKILL.md" && grep -qF "name: release-dry-run" ".rulesync/skills/release-dry-run/SKILL.md" && grep -qF "name: release" ".rulesync/skills/release/SKILL.md" && grep -qF "name: security-scan-diff" ".rulesync/skills/security-scan-diff/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.rulesync/skills/clean-worktrees/SKILL.md b/.rulesync/skills/clean-worktrees/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: clean-worktrees
 description: "Clean git worktrees created by git-worktree-runner"
 targets:
   - "*"
diff --git a/.rulesync/skills/create-issue/SKILL.md b/.rulesync/skills/create-issue/SKILL.md
@@ -1,9 +1,10 @@
 ---
-targets:
-  - "*"
+name: create-issue
 description: >-
   Create a GitHub issue with detailed description, purpose, and appropriate
   labels
+targets:
+  - "*"
 ---
 
 # Create GitHub Issue
diff --git a/.rulesync/skills/explain-pr/SKILL.md b/.rulesync/skills/explain-pr/SKILL.md
@@ -1,7 +1,8 @@
 ---
+name: explain-pr
+description: "Explain a PR: the background problem and the proposed solution"
 targets:
   - "*"
-description: "Explain a PR: the background problem and the proposed solution"
 ---
 
 target_pr = $ARGUMENTS
diff --git a/.rulesync/skills/merge-pr/SKILL.md b/.rulesync/skills/merge-pr/SKILL.md
@@ -1,7 +1,8 @@
 ---
+name: merge-pr
+description: Merge a pull request using gh pr merge --admin
 targets:
   - "*"
-description: Merge a pull request using gh pr merge --admin
 ---
 
 # Merge Pull Request
diff --git a/.rulesync/skills/post-review-comment/SKILL.md b/.rulesync/skills/post-review-comment/SKILL.md
@@ -1,9 +1,10 @@
 ---
-targets:
-  - "*"
+name: post-review-comment
 description: >-
   Post line-level review comments and an overall review comment on a PR in
   English with a natural, concise writing style
+targets:
+  - "*"
 ---
 
 target_pr = $ARGUMENTS
diff --git a/.rulesync/skills/release-dry-run/SKILL.md b/.rulesync/skills/release-dry-run/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: release-dry-run
 description: "Dry run for release: summarize changes since last release and suggest version bump."
 targets:
   - "*"
diff --git a/.rulesync/skills/release/SKILL.md b/.rulesync/skills/release/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: release
 description: "Release a new version of the project."
 targets:
   - "*"
diff --git a/.rulesync/skills/security-scan-diff/SKILL.md b/.rulesync/skills/security-scan-diff/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: security-scan-diff
 description: "Scan for malicious code in git diff between a tag/commit and HEAD"
 targets:
   - "*"
PATCH

echo "Gold patch applied."
