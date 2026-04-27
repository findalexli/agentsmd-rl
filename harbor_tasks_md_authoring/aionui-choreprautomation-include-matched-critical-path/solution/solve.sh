#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aionui

# Idempotency guard
if grep -qF "Parse the `<!-- automation-result -->` block from the cached comment. Set `CONCL" ".claude/skills/pr-automation/SKILL.md" && grep -qF "CRITICAL_FILES=$(git diff origin/<baseRefName>...HEAD --name-only | grep -E \"$CR" ".claude/skills/pr-review/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/pr-automation/SKILL.md b/.claude/skills/pr-automation/SKILL.md
@@ -244,9 +244,11 @@ BASE_REF=$(gh pr view <PR_NUMBER> --json baseRefName --jq '.baseRefName')
 FILES_CHANGED=$(git diff origin/${BASE_REF}...FETCH_HEAD --name-only | wc -l | tr -d ' ')
 # CRITICAL_PATH_PATTERN: defined in Configuration section above
 HAS_CRITICAL=false
-[ -n "$CRITICAL_PATH_PATTERN" ] && \
-  git diff origin/${BASE_REF}...FETCH_HEAD --name-only | grep -qE "$CRITICAL_PATH_PATTERN" && \
-  HAS_CRITICAL=true
+CRITICAL_FILES=""
+if [ -n "$CRITICAL_PATH_PATTERN" ]; then
+  CRITICAL_FILES=$(git diff origin/${BASE_REF}...FETCH_HEAD --name-only | grep -E "$CRITICAL_PATH_PATTERN")
+  [ -n "$CRITICAL_FILES" ] && HAS_CRITICAL=true
+fi
 
 if [ "$FILES_CHANGED" -gt 50 ] || [ "$HAS_CRITICAL" = "true" ]; then
   NEEDS_HUMAN_REVIEW=true
@@ -501,15 +503,17 @@ BASE_REF=$(gh pr view <PR_NUMBER> --json baseRefName --jq '.baseRefName')
 FILES_CHANGED=$(git diff origin/${BASE_REF}...FETCH_HEAD --name-only | wc -l | tr -d ' ')
 
 # CRITICAL_PATH_PATTERN: defined in Configuration section above
+CRITICAL_FILES=""
 if [ -n "$CRITICAL_PATH_PATTERN" ]; then
-  HAS_CRITICAL=$(git diff origin/${BASE_REF}...FETCH_HEAD --name-only \
-    | grep -qE "$CRITICAL_PATH_PATTERN" && echo true || echo false)
+  CRITICAL_FILES=$(git diff origin/${BASE_REF}...FETCH_HEAD --name-only \
+    | grep -E "$CRITICAL_PATH_PATTERN")
+  [ -n "$CRITICAL_FILES" ] && HAS_CRITICAL=true || HAS_CRITICAL=false
 else
   HAS_CRITICAL=false
 fi
 ```
 
-Save `FILES_CHANGED` and `HAS_CRITICAL` for later steps.
+Save `FILES_CHANGED`, `HAS_CRITICAL`, and `CRITICAL_FILES` for later steps.
 
 ### Step 6 — Run pr-review (automation mode)
 
@@ -539,7 +543,7 @@ gh pr view <PR_NUMBER> --json comments \
   --jq '[.comments[] | select(.body | startswith("<!-- pr-review-bot -->"))] | last | .body'
 ```
 
-Parse the `<!-- automation-result -->` block from the cached comment. Set `CONCLUSION` and `IS_CRITICAL_PATH` from it, then **skip to Step 7** (do not run pr-review again).
+Parse the `<!-- automation-result -->` block from the cached comment. Set `CONCLUSION`, `IS_CRITICAL_PATH`, and `CRITICAL_PATH_FILES` from it, then **skip to Step 7** (do not run pr-review again).
 
 Log: `[pr-automation] PR #<PR_NUMBER> has valid cached review (no new commits since review) — skipping re-review.`
 
@@ -555,11 +559,16 @@ After pr-review completes, parse the `<!-- automation-result -->` block:
 <!-- automation-result -->
 CONCLUSION: APPROVED | CONDITIONAL | REJECTED | CI_FAILED | CI_NOT_READY
 IS_CRITICAL_PATH: true | false
+CRITICAL_PATH_FILES:
+- file1
+- file2
 PR_NUMBER: <number>
 <!-- /automation-result -->
 ```
 
-Save `CONCLUSION` and `IS_CRITICAL_PATH` (override Step 5 value if different).
+When `IS_CRITICAL_PATH` is false, `CRITICAL_PATH_FILES` is `(none)`.
+
+Save `CONCLUSION`, `IS_CRITICAL_PATH`, and `CRITICAL_PATH_FILES` (override Step 5 values if different).
 
 If block is missing: set `CONCLUSION=REJECTED`, log the error, continue to Step 7.
 
@@ -579,11 +588,23 @@ When `NEEDS_HUMAN_REVIEW=true`, route to human review regardless of CONCLUSION (
 
 1. Post comment:
 
+   When `IS_CRITICAL_PATH=true`, include the matched files in the comment:
+
    ```bash
+   # Build critical path file list for the comment
+   if [ -n "$CRITICAL_FILES" ]; then
+     CRITICAL_LIST=$(echo "$CRITICAL_FILES" | sed 's/^/   - `/' | sed 's/$/`/')
+     CRITICAL_SECTION="
+   > 📂 **命中核心路径的文件：**
+   ${CRITICAL_LIST}"
+   else
+     CRITICAL_SECTION=""
+   fi
+
    gh pr comment <PR_NUMBER> --body "<!-- pr-automation-bot -->
    ✅ 已自动 review，代码无阻塞性问题。
 
-   > ⚠️ **本 PR 规模较大（改动文件 ${FILES_CHANGED} 个）或涉及核心路径，请人工确认后合并。**"
+   > ⚠️ **本 PR 规模较大（改动文件 ${FILES_CHANGED} 个）或涉及核心路径，请人工确认后合并。**${CRITICAL_SECTION}"
    ```
 
 2. Update labels:
diff --git a/.claude/skills/pr-review/SKILL.md b/.claude/skills/pr-review/SKILL.md
@@ -95,6 +95,7 @@ gh pr view <PR_NUMBER> --json statusCheckRollup \
   <!-- automation-result -->
   CONCLUSION: CI_NOT_READY
   IS_CRITICAL_PATH: false
+  CRITICAL_PATH_FILES: (none)
   PR_NUMBER: <PR_NUMBER>
   <!-- /automation-result -->
   ```
@@ -119,6 +120,7 @@ gh pr view <PR_NUMBER> --json statusCheckRollup \
   <!-- automation-result -->
   CONCLUSION: CI_FAILED
   IS_CRITICAL_PATH: false
+  CRITICAL_PATH_FILES: (none)
   PR_NUMBER: <PR_NUMBER>
   <!-- /automation-result -->
   ```
@@ -425,15 +427,21 @@ Map the review conclusion to CONCLUSION value based on the **highest severity is
 **Key rule:** If all issues are LOW (or there are no issues), emit `APPROVED` even when the human-facing verdict says "有条件批准". `pr-fix` explicitly skips LOW issues, so triggering a fix session for LOW-only reviews wastes a round with no actionable outcome.
 
 Determine `IS_CRITICAL_PATH` using the `CRITICAL_PATH_PATTERN` env var (defined in `scripts/pr-automation.conf`, passed by daemon at runtime).
-When a pattern is defined, check:
+When a pattern is defined, check and capture matched files:
 
 ```bash
 # CRITICAL_PATH_PATTERN is an env var — set by pr-automation daemon or manually
 if [ -n "$CRITICAL_PATH_PATTERN" ]; then
   cd "$WORKTREE_DIR"
-  git diff origin/<baseRefName>...HEAD --name-only | grep -qE "$CRITICAL_PATH_PATTERN" && echo true || echo false
+  CRITICAL_FILES=$(git diff origin/<baseRefName>...HEAD --name-only | grep -E "$CRITICAL_PATH_PATTERN")
+  if [ -n "$CRITICAL_FILES" ]; then
+    IS_CRITICAL_PATH=true
+  else
+    IS_CRITICAL_PATH=false
+  fi
 else
-  echo false
+  IS_CRITICAL_PATH=false
+  CRITICAL_FILES=""
 fi
 ```
 
@@ -443,10 +451,24 @@ Output:
 <!-- automation-result -->
 CONCLUSION: APPROVED
 IS_CRITICAL_PATH: false
+CRITICAL_PATH_FILES: (none)
 PR_NUMBER: 123
 <!-- /automation-result -->
 ```
 
+When `IS_CRITICAL_PATH` is true, list matched files one per line:
+
+```
+<!-- automation-result -->
+CONCLUSION: APPROVED
+IS_CRITICAL_PATH: true
+CRITICAL_PATH_FILES:
+- docs/feature/extension-market/agent-hub-requirements.md
+- docs/feature/extension-market/research/architecture.md
+PR_NUMBER: 456
+<!-- /automation-result -->
+```
+
 ### Step 9 — Cleanup
 
 Remove the worktree. No branch switching needed — the main repo was never touched.
PATCH

echo "Gold patch applied."
