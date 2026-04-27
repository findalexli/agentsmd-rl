#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "If none resolve, ask the user to specify the target branch. Use the platform's b" "plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md
@@ -60,11 +60,73 @@ command git push -u origin HEAD
 
 ### Step 6: Write the PR description
 
+Before writing, determine the **base branch** and gather the **full branch scope**. The working-tree diff from Step 1 only shows uncommitted changes at invocation time -- the PR description must cover **all commits** that will appear in the PR.
+
+#### Detect the base branch and remote
+
+Resolve the base branch **and** the remote that hosts it. In fork-based PRs the base repository may correspond to a remote other than `origin` (commonly `upstream`).
+
+Use this fallback chain. Stop at the first that succeeds:
+
+1. **PR metadata** (if an existing PR was found in Step 3):
+   ```bash
+   command gh pr view --json baseRefName,url
+   ```
+   Extract `baseRefName` as the base branch name. The PR URL contains the base repository (`https://github.com/<owner>/<repo>/pull/...`). Determine which local remote corresponds to that repository:
+   ```bash
+   command git remote -v
+   ```
+   Match the `owner/repo` from the PR URL against the fetch URLs. Use the matching remote as the base remote. If no remote matches, fall back to `origin`.
+2. **`origin/HEAD` symbolic ref:**
+   ```bash
+   command git symbolic-ref --quiet --short refs/remotes/origin/HEAD
+   ```
+   Strip the `origin/` prefix from the result. Use `origin` as the base remote.
+3. **GitHub default branch metadata:**
+   ```bash
+   command gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
+   ```
+   Use `origin` as the base remote.
+4. **Common branch names** -- check `main`, `master`, `develop`, `trunk` in order. Use the first that exists on the remote:
+   ```bash
+   command git rev-parse --verify origin/<candidate>
+   ```
+   Use `origin` as the base remote.
+
+If none resolve, ask the user to specify the target branch. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply.
+
+#### Gather the branch scope
+
+Once the base branch and remote are known:
+
+1. Verify the remote-tracking ref exists locally and fetch if needed:
+   ```bash
+   command git rev-parse --verify <base-remote>/<base-branch>
+   ```
+   If this fails (ref missing or stale), fetch it:
+   ```bash
+   command git fetch --no-tags <base-remote> <base-branch>
+   ```
+2. Find the merge base:
+   ```bash
+   command git merge-base <base-remote>/<base-branch> HEAD
+   ```
+2. List all commits unique to this branch:
+   ```bash
+   command git log --oneline <merge-base>..HEAD
+   ```
+3. Get the full diff a reviewer will see:
+   ```bash
+   command git diff <merge-base>...HEAD
+   ```
+
+Use the full branch diff and commit list as the basis for the PR description -- not the working-tree diff from Step 1.
+
 This is the most important step. The description must be **adaptive** -- its depth should match the complexity of the change. A one-line bugfix does not need a table of performance results. A large architectural change should not be a bullet list.
 
 #### Sizing the change
 
-Assess the PR along two axes before writing:
+Assess the PR along two axes before writing, based on the full branch diff:
 
 - **Size**: How many files changed? How large is the diff?
 - **Complexity**: Is this a straightforward change (rename, dependency bump, typo fix) or does it involve design decisions, trade-offs, new patterns, or cross-cutting concerns?
PATCH

echo "Gold patch applied."
