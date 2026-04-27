#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "printf '=== STATUS ===\\n'; git status; printf '\\n=== DIFF ===\\n'; git diff HEAD;" "plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md
@@ -13,30 +13,6 @@ If the user is asking to update, refresh, or rewrite an existing PR description
 
 For description-only updates, follow the Description Update workflow below. Otherwise, follow the full workflow.
 
-## Reusable PR probe
-
-When checking whether the current branch already has a PR, keep using current-branch `gh pr view` semantics. Do **not** switch to `gh pr list --head "<branch>"` just to avoid the no-PR exit path. That branch-name search can select the wrong PR in multi-fork repos.
-
-Also do **not** run bare `gh pr view --json ...` in a way that lets the shell tool render the expected no-PR state as a red failed step. Capture the output and exit code yourself so you can interpret "no PR for this branch" as normal workflow state:
-
-```bash
-if PR_VIEW_OUTPUT=$(gh pr view --json url,title,state 2>&1); then
-  PR_VIEW_EXIT=0
-else
-  PR_VIEW_EXIT=$?
-fi
-printf '%s\n__GH_PR_VIEW_EXIT__=%s\n' "$PR_VIEW_OUTPUT" "$PR_VIEW_EXIT"
-```
-
-Interpret the result this way:
-
-- `__GH_PR_VIEW_EXIT__=0` and JSON with `state: OPEN` -> an open PR exists for the current branch
-- `__GH_PR_VIEW_EXIT__=0` and JSON with a non-OPEN state -> treat as no open PR
-- non-zero exit with output indicating `no pull requests found for branch` -> expected no-PR state
-- any other non-zero exit -> real error (auth, network, repo config, etc.)
-
----
-
 ## Context
 
 **If you are not Claude Code**, skip to the "Context fallback" section below and run the command there to gather context.
@@ -56,10 +32,10 @@ Interpret the result this way:
 !`git log --oneline -10`
 
 **Remote default branch:**
-!`git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || echo '__DEFAULT_BRANCH_UNRESOLVED__'`
+!`git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || echo 'DEFAULT_BRANCH_UNRESOLVED'`
 
 **Existing PR check:**
-!`PR_OUT=$(gh pr view --json url,title,state 2>&1); PR_EXIT=$?; printf '%s\n__GH_PR_VIEW_EXIT__=%s\n' "$PR_OUT" "$PR_EXIT"`
+!`gh pr view --json url,title,state 2>/dev/null || echo 'NO_OPEN_PR'`
 
 ### Context fallback
 
@@ -68,11 +44,9 @@ Interpret the result this way:
 Run this single command to gather all context:
 
 ```bash
-printf '=== STATUS ===\n'; git status; printf '\n=== DIFF ===\n'; git diff HEAD; printf '\n=== BRANCH ===\n'; git branch --show-current; printf '\n=== LOG ===\n'; git log --oneline -10; printf '\n=== DEFAULT_BRANCH ===\n'; git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || echo '__DEFAULT_BRANCH_UNRESOLVED__'; printf '\n=== PR_CHECK ===\n'; PR_OUT=$(gh pr view --json url,title,state 2>&1); PR_EXIT=$?; printf '%s\n__GH_PR_VIEW_EXIT__=%s\n' "$PR_OUT" "$PR_EXIT"
+printf '=== STATUS ===\n'; git status; printf '\n=== DIFF ===\n'; git diff HEAD; printf '\n=== BRANCH ===\n'; git branch --show-current; printf '\n=== LOG ===\n'; git log --oneline -10; printf '\n=== DEFAULT_BRANCH ===\n'; git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || echo 'DEFAULT_BRANCH_UNRESOLVED'; printf '\n=== PR_CHECK ===\n'; gh pr view --json url,title,state 2>/dev/null || echo 'NO_OPEN_PR'
 ```
 
-Interpret the PR check result using the Reusable PR probe rules above.
-
 ---
 
 ## Description Update workflow
@@ -87,12 +61,7 @@ If the user declines, stop.
 
 Use the current branch and existing PR check from the context above. If the current branch is empty (detached HEAD), report that there is no branch to update and stop.
 
-Interpret the PR check result using the Reusable PR probe rules above:
-
-- If it returns PR data with `state: OPEN`, an open PR exists for the current branch.
-- If it returns PR data with a non-OPEN state (CLOSED, MERGED), treat this as "no open PR." Report that no open PR exists for this branch and stop.
-- If it exits non-zero and the output indicates that no pull request exists for the current branch, treat that as the normal "no PR for this branch" state. Report that no open PR exists for this branch and stop.
-- If it errors for another reason (auth, network, repo config), report the error and stop.
+If the existing PR check returned JSON with `state: OPEN`, an open PR exists — proceed to DU-3. Otherwise (`NO_OPEN_PR` or a non-OPEN state), report no open PR and stop.
 
 ### DU-3: Write and apply the updated description
 
@@ -125,7 +94,7 @@ Report the PR URL.
 
 Use the context above (git status, working tree diff, current branch, recent commits, remote default branch, and existing PR check). All data needed for this step and Step 3 is already available -- do not re-run those commands.
 
-The remote default branch value returns something like `origin/main`. Strip the `origin/` prefix to get the branch name. If it returned `__DEFAULT_BRANCH_UNRESOLVED__` or a bare `HEAD`, try:
+The remote default branch value returns something like `origin/main`. Strip the `origin/` prefix to get the branch name. If it returned `DEFAULT_BRANCH_UNRESOLVED` or a bare `HEAD`, try:
 
 ```bash
 gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
@@ -164,12 +133,7 @@ Follow this priority order for commit messages *and* PR titles:
 
 Use the current branch and existing PR check from the context above. If the current branch is empty, report that the workflow is in detached HEAD state and stop.
 
-Interpret the PR check result using the Reusable PR probe rules:
-
-- If it **returns PR data with `state: OPEN`**, an open PR exists for the current branch. Note the URL and continue to Step 4 (commit) and Step 5 (push). Then skip to Step 7 (existing PR flow) instead of creating a new PR.
-- If it **returns PR data with a non-OPEN state** (CLOSED, MERGED), treat this the same as "no PR exists" -- the previous PR is done and a new one is needed. Continue to Step 4 through Step 8 as normal.
-- If it **exits non-zero and the output indicates that no pull request exists for the current branch**, no PR exists. Continue to Step 4 through Step 8 as normal.
-- If it **errors** (auth, network, repo config), report the error to the user and stop.
+If the existing PR check returned JSON with `state: OPEN`, note the URL — continue to Step 4 and Step 5, then skip to Step 7 (existing PR flow). Otherwise (`NO_OPEN_PR` or a non-OPEN state), continue to Step 4 through Step 8.
 
 ### Step 4: Branch, stage, and commit
 
@@ -208,7 +172,7 @@ Use this fallback chain. Stop at the first that succeeds:
    git remote -v
    ```
    Match the `owner/repo` from the PR URL against the fetch URLs. Use the matching remote as the base remote. If no remote matches, fall back to `origin`.
-2. **Remote default branch from context above:** If the remote default branch resolved (not `__DEFAULT_BRANCH_UNRESOLVED__`), strip the `origin/` prefix and use that. Use `origin` as the base remote.
+2. **Remote default branch from context above:** If the remote default branch resolved (not `DEFAULT_BRANCH_UNRESOLVED`), strip the `origin/` prefix and use that. Use `origin` as the base remote.
 3. **GitHub default branch metadata:**
    ```bash
    gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
PATCH

echo "Gold patch applied."
