#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "printf '=== STATUS ===\\n'; git status; printf '\\n=== DIFF ===\\n'; git diff HEAD;" "plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md" && grep -qF "If the current branch from the context above is `main`, `master`, or the resolve" "plugins/compound-engineering/skills/git-commit/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md
@@ -37,36 +37,57 @@ Interpret the result this way:
 
 ---
 
-## Description Update workflow
+## Context
 
-### DU-1: Confirm intent
+**If you are not Claude Code**, skip to the "Context fallback" section below and run the command there to gather context.
 
-Ask the user to confirm: "Update the PR description for this branch?" Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the question and wait for the user's reply.
+**If you are Claude Code**, the six labeled sections below (Git status, Working tree diff, Current branch, Recent commits, Remote default branch, Existing PR check) contain pre-populated data. Use them directly throughout this skill -- do not re-run these commands.
 
-If the user declines, stop.
+**Git status:**
+!`git status`
 
-### DU-2: Find the PR
+**Working tree diff:**
+!`git diff HEAD`
 
-Run these commands to identify the branch and locate the PR:
+**Current branch:**
+!`git branch --show-current`
 
-```bash
-git branch --show-current
-```
+**Recent commits:**
+!`git log --oneline -10`
+
+**Remote default branch:**
+!`git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || echo '__DEFAULT_BRANCH_UNRESOLVED__'`
 
-If empty (detached HEAD), report that there is no branch to update and stop.
+**Existing PR check:**
+!`PR_OUT=$(gh pr view --json url,title,state 2>&1); PR_EXIT=$?; printf '%s\n__GH_PR_VIEW_EXIT__=%s\n' "$PR_OUT" "$PR_EXIT"`
 
-Otherwise, check for an existing open PR:
+### Context fallback
+
+**If you are Claude Code, skip this section — the data above is already available.**
+
+Run this single command to gather all context:
 
 ```bash
-if PR_VIEW_OUTPUT=$(gh pr view --json url,title,state 2>&1); then
-  PR_VIEW_EXIT=0
-else
-  PR_VIEW_EXIT=$?
-fi
-printf '%s\n__GH_PR_VIEW_EXIT__=%s\n' "$PR_VIEW_OUTPUT" "$PR_VIEW_EXIT"
+printf '=== STATUS ===\n'; git status; printf '\n=== DIFF ===\n'; git diff HEAD; printf '\n=== BRANCH ===\n'; git branch --show-current; printf '\n=== LOG ===\n'; git log --oneline -10; printf '\n=== DEFAULT_BRANCH ===\n'; git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || echo '__DEFAULT_BRANCH_UNRESOLVED__'; printf '\n=== PR_CHECK ===\n'; PR_OUT=$(gh pr view --json url,title,state 2>&1); PR_EXIT=$?; printf '%s\n__GH_PR_VIEW_EXIT__=%s\n' "$PR_OUT" "$PR_EXIT"
 ```
 
-Interpret the result using the Reusable PR probe rules above:
+Interpret the PR check result using the Reusable PR probe rules above.
+
+---
+
+## Description Update workflow
+
+### DU-1: Confirm intent
+
+Ask the user to confirm: "Update the PR description for this branch?" Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the question and wait for the user's reply.
+
+If the user declines, stop.
+
+### DU-2: Find the PR
+
+Use the current branch and existing PR check from the context above. If the current branch is empty (detached HEAD), report that there is no branch to update and stop.
+
+Interpret the PR check result using the Reusable PR probe rules above:
 
 - If it returns PR data with `state: OPEN`, an open PR exists for the current branch.
 - If it returns PR data with a non-OPEN state (CLOSED, MERGED), treat this as "no open PR." Report that no open PR exists for this branch and stop.
@@ -102,35 +123,25 @@ Report the PR URL.
 
 ### Step 1: Gather context
 
-Run these commands.
-
-```bash
-git status
-git diff HEAD
-git branch --show-current
-git log --oneline -10
-git rev-parse --abbrev-ref origin/HEAD
-```
+Use the context above (git status, working tree diff, current branch, recent commits, remote default branch, and existing PR check). All data needed for this step and Step 3 is already available -- do not re-run those commands.
 
-The last command returns the remote default branch (e.g., `origin/main`). Strip the `origin/` prefix to get the branch name. If the command fails or returns a bare `HEAD`, try:
+The remote default branch value returns something like `origin/main`. Strip the `origin/` prefix to get the branch name. If it returned `__DEFAULT_BRANCH_UNRESOLVED__` or a bare `HEAD`, try:
 
 ```bash
 gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
 ```
 
 If both fail, fall back to `main`.
 
-Run `git branch --show-current`. If it returns an empty result, the repository is in detached HEAD state. Explain that a branch is required before committing and pushing. Ask whether to create a feature branch now. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply.
+If the current branch from the context above is empty, the repository is in detached HEAD state. Explain that a branch is required before committing and pushing. Ask whether to create a feature branch now. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply.
 
 - If the user agrees, derive a descriptive branch name from the change content, create it with `git checkout -b <branch-name>`, then run `git branch --show-current` again and use that result as the current branch name for the rest of the workflow.
 - If the user declines, stop.
 
-If the `git status` result from this step shows a clean working tree (no staged, modified, or untracked files), check whether there are unpushed commits or a missing PR before stopping:
+If the git status from the context above shows a clean working tree (no staged, modified, or untracked files), check whether there are unpushed commits or a missing PR before stopping. The current branch and existing PR check are already available from the context above. Additionally:
 
-1. Run `git branch --show-current` to get the current branch name.
-2. Run `git rev-parse --abbrev-ref --symbolic-full-name @{u}` to check whether an upstream is configured.
-3. If the command succeeds, run `git log <upstream>..HEAD --oneline` using the upstream name from the previous command.
-4. If an upstream is configured, check for an existing PR using the method in Step 3.
+1. Run `git rev-parse --abbrev-ref --symbolic-full-name @{u}` to check whether an upstream is configured.
+2. If the command succeeds, run `git log <upstream>..HEAD --oneline` using the upstream name from the previous command.
 
 - If the current branch is `main`, `master`, or the resolved default branch from Step 1 and there is **no upstream** or there are **unpushed commits**, explain that pushing now would use the default branch directly. Ask whether to create a feature branch first. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply.
 - If the user agrees, derive a descriptive branch name from the change content, create it with `git checkout -b <branch-name>`, then continue from Step 5 (push).
@@ -151,20 +162,9 @@ Follow this priority order for commit messages *and* PR titles:
 
 ### Step 3: Check for existing PR
 
-Run `git branch --show-current` to get the current branch name. If it returns an empty result here, report that the workflow is still in detached HEAD state and stop.
-
-Then check for an existing open PR:
-
-```bash
-if PR_VIEW_OUTPUT=$(gh pr view --json url,title,state 2>&1); then
-  PR_VIEW_EXIT=0
-else
-  PR_VIEW_EXIT=$?
-fi
-printf '%s\n__GH_PR_VIEW_EXIT__=%s\n' "$PR_VIEW_OUTPUT" "$PR_VIEW_EXIT"
-```
+Use the current branch and existing PR check from the context above. If the current branch is empty, report that the workflow is in detached HEAD state and stop.
 
-Interpret the result using the Reusable PR probe rules above:
+Interpret the PR check result using the Reusable PR probe rules:
 
 - If it **returns PR data with `state: OPEN`**, an open PR exists for the current branch. Note the URL and continue to Step 4 (commit) and Step 5 (push). Then skip to Step 7 (existing PR flow) instead of creating a new PR.
 - If it **returns PR data with a non-OPEN state** (CLOSED, MERGED), treat this the same as "no PR exists" -- the previous PR is done and a new one is needed. Continue to Step 4 through Step 8 as normal.
@@ -173,10 +173,15 @@ Interpret the result using the Reusable PR probe rules above:
 
 ### Step 4: Branch, stage, and commit
 
-1. Run `git branch --show-current`. If it returns `main`, `master`, or the resolved default branch from Step 1, create a descriptive feature branch first with `git checkout -b <branch-name>`. Derive the branch name from the change content.
+1. If the current branch from the context above is `main`, `master`, or the resolved default branch from Step 1, create a descriptive feature branch first with `git checkout -b <branch-name>`. Derive the branch name from the change content.
 2. Before staging everything together, scan the changed files for naturally distinct concerns. If modified files clearly group into separate logical changes (e.g., a refactor in one set of files and a new feature in another), create separate commits for each group. Keep this lightweight -- group at the **file level only** (no `git add -p`), split only when obvious, and aim for two or three logical commits at most. If it's ambiguous, one commit is fine.
-3. Stage relevant files by name. Avoid `git add -A` or `git add .` to prevent accidentally including sensitive files.
-4. Commit following the conventions from Step 2. Use a heredoc for the message.
+3. For each commit group, stage and commit in a single call. Avoid `git add -A` or `git add .` to prevent accidentally including sensitive files. Follow the conventions from Step 2. Use a heredoc for the message:
+   ```bash
+   git add file1 file2 file3 && git commit -m "$(cat <<'EOF'
+   commit message here
+   EOF
+   )"
+   ```
 
 ### Step 5: Push
 
@@ -203,11 +208,7 @@ Use this fallback chain. Stop at the first that succeeds:
    git remote -v
    ```
    Match the `owner/repo` from the PR URL against the fetch URLs. Use the matching remote as the base remote. If no remote matches, fall back to `origin`.
-2. **`origin/HEAD` symbolic ref:**
-   ```bash
-   git symbolic-ref --quiet --short refs/remotes/origin/HEAD
-   ```
-   Strip the `origin/` prefix from the result. Use `origin` as the base remote.
+2. **Remote default branch from context above:** If the remote default branch resolved (not `__DEFAULT_BRANCH_UNRESOLVED__`), strip the `origin/` prefix and use that. Use `origin` as the base remote.
 3. **GitHub default branch metadata:**
    ```bash
    gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
@@ -223,28 +224,19 @@ If none resolve, ask the user to specify the target branch. Use the platform's b
 
 #### Gather the branch scope
 
-Once the base branch and remote are known:
+Once the base branch and remote are known, gather the full scope in as few calls as possible.
 
-1. Verify the remote-tracking ref exists locally and fetch if needed:
-   ```bash
-   git rev-parse --verify <base-remote>/<base-branch>
-   ```
-   If this fails (ref missing or stale), fetch it:
-   ```bash
-   git fetch --no-tags <base-remote> <base-branch>
-   ```
-2. Find the merge base:
-   ```bash
-   git merge-base <base-remote>/<base-branch> HEAD
-   ```
-3. List all commits unique to this branch:
-   ```bash
-   git log --oneline <merge-base>..HEAD
-   ```
-4. Get the full diff a reviewer will see:
-   ```bash
-   git diff <merge-base>...HEAD
-   ```
+First, verify the remote-tracking ref exists and fetch if needed:
+
+```bash
+git rev-parse --verify <base-remote>/<base-branch> 2>/dev/null || git fetch --no-tags <base-remote> <base-branch>
+```
+
+Then gather the merge base, commit list, and full diff in a single call:
+
+```bash
+MERGE_BASE=$(git merge-base <base-remote>/<base-branch> HEAD) && echo "MERGE_BASE=$MERGE_BASE" && echo '=== COMMITS ===' && git log --oneline $MERGE_BASE..HEAD && echo '=== DIFF ===' && git diff $MERGE_BASE...HEAD
+```
 
 Use the full branch diff and commit list as the basis for the PR description -- not the working-tree diff from Step 1.
 
diff --git a/plugins/compound-engineering/skills/git-commit/SKILL.md b/plugins/compound-engineering/skills/git-commit/SKILL.md
@@ -7,31 +7,56 @@ description: Create a git commit with a clear, value-communicating message. Use
 
 Create a single, well-crafted git commit from the current working tree changes.
 
-## Workflow
+## Context
 
-### Step 1: Gather context
+**If you are not Claude Code**, skip to the "Context fallback" section below and run the command there to gather context.
+
+**If you are Claude Code**, the five labeled sections below (Git status, Working tree diff, Current branch, Recent commits, Remote default branch) contain pre-populated data. Use them directly throughout this skill -- do not re-run these commands.
+
+**Git status:**
+!`git status`
+
+**Working tree diff:**
+!`git diff HEAD`
+
+**Current branch:**
+!`git branch --show-current`
+
+**Recent commits:**
+!`git log --oneline -10`
+
+**Remote default branch:**
+!`git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || echo '__DEFAULT_BRANCH_UNRESOLVED__'`
+
+### Context fallback
 
-Run these commands to understand the current state.
+**If you are Claude Code, skip this section — the data above is already available.**
+
+Run this single command to gather all context:
 
 ```bash
-git status
-git diff HEAD
-git branch --show-current
-git log --oneline -10
-git rev-parse --abbrev-ref origin/HEAD
+printf '=== STATUS ===\n'; git status; printf '\n=== DIFF ===\n'; git diff HEAD; printf '\n=== BRANCH ===\n'; git branch --show-current; printf '\n=== LOG ===\n'; git log --oneline -10; printf '\n=== DEFAULT_BRANCH ===\n'; git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || echo '__DEFAULT_BRANCH_UNRESOLVED__'
 ```
 
-The last command returns the remote default branch (e.g., `origin/main`). Strip the `origin/` prefix to get the branch name. If the command fails or returns a bare `HEAD`, try:
+---
+
+## Workflow
+
+### Step 1: Gather context
+
+Use the context above (git status, working tree diff, current branch, recent commits, remote default branch). All data needed for this step is already available -- do not re-run those commands.
+
+The remote default branch value returns something like `origin/main`. Strip the `origin/` prefix to get the branch name. If it returned `__DEFAULT_BRANCH_UNRESOLVED__` or a bare `HEAD`, try:
 
 ```bash
 gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
 ```
 
 If both fail, fall back to `main`.
 
-If the `git status` result from this step shows a clean working tree (no staged, modified, or untracked files), report that there is nothing to commit and stop.
+If the git status from the context above shows a clean working tree (no staged, modified, or untracked files), report that there is nothing to commit and stop.
 
-Run `git branch --show-current`. If it returns an empty result, the repository is in detached HEAD state. Explain that a branch is required before committing if the user wants this work attached to a branch. Ask whether to create a feature branch now. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply before proceeding.
+If the current branch from the context above is empty, the repository is in detached HEAD state. Explain that a branch is required before committing if the user wants this work attached to a branch. Ask whether to create a feature branch now. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply before proceeding.
 
 - If the user chooses to create a branch, derive the name from the change content, create it with `git checkout -b <branch-name>`, then run `git branch --show-current` again and use that result as the current branch name for the rest of the workflow.
 - If the user declines, continue with the detached HEAD commit.
@@ -55,18 +80,16 @@ Keep this lightweight:
 
 ### Step 4: Stage and commit
 
-Run `git branch --show-current`. If it returns `main`, `master`, or the resolved default branch from Step 1, warn the user and ask whether to continue committing here or create a feature branch first. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply before proceeding. If the user chooses to create a branch, derive the name from the change content, create it with `git checkout -b <branch-name>`, then run `git branch --show-current` again and use that result as the current branch name for the rest of the workflow.
-
-Stage the relevant files. Prefer staging specific files by name over `git add -A` or `git add .` to avoid accidentally including sensitive files (.env, credentials) or unrelated changes.
+If the current branch from the context above is `main`, `master`, or the resolved default branch from Step 1, warn the user and ask whether to continue committing here or create a feature branch first. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply before proceeding. If the user chooses to create a branch, derive the name from the change content, create it with `git checkout -b <branch-name>`, then continue.
 
 Write the commit message:
 - **Subject line**: Concise, imperative mood, focused on *why* not *what*. Follow the convention determined in Step 2.
 - **Body** (when needed): Add a body separated by a blank line for non-trivial changes. Explain motivation, trade-offs, or anything a future reader would need. Omit the body for obvious single-purpose changes.
 
-Use a heredoc to preserve formatting:
+For each commit group, stage and commit in a single call. Prefer staging specific files by name over `git add -A` or `git add .` to avoid accidentally including sensitive files (.env, credentials) or unrelated changes. Use a heredoc to preserve formatting:
 
 ```bash
-git commit -m "$(cat <<'EOF'
+git add file1 file2 file3 && git commit -m "$(cat <<'EOF'
 type(scope): subject line here
 
 Optional body explaining why this change was made,
PATCH

echo "Gold patch applied."
