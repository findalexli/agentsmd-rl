#!/usr/bin/env bash
set -euo pipefail

cd /workspace/babylon.js

# Idempotency guard
if grep -qF "powershell -Command \"Add-Type -AssemblyName System.Windows.Forms; [System.Window" ".github/skills/create-pr/SKILL.md" && grep -qF "powershell -Command \"Add-Type -AssemblyName System.Windows.Forms; [System.Window" ".github/skills/monitor-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/create-pr/SKILL.md b/.github/skills/create-pr/SKILL.md
@@ -0,0 +1,482 @@
+---
+name: create-pr
+description: |
+    Orchestrates the full PR lifecycle: merge upstream, create draft PR,
+    self code review, mark ready, monitor, and iterate on fixes.
+    Can also monitor and iterate on an existing PR.
+    Input: [--push-remote <fork>] [--upstream-remote <remote>] [--base <branch>] [--merge] [--mode automatic|interactive] [--pr <number>]
+argument-hint: "[--push-remote <fork>] [--upstream-remote <remote>] [--base <branch>] [--merge] [--mode automatic|interactive] [--pr <number>]"
+---
+
+# Create PR
+
+Orchestrator skill that creates a PR and shepherds it through review. It
+invokes other skills as sub-agents and does its own work between them.
+
+## Input
+
+Parse `$ARGUMENTS`:
+
+| Argument                   | Description                                                                                                                 |
+| -------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
+| `--push-remote <fork>`     | Git remote (user's fork) to push the branch to. If omitted, detect and prompt.                                              |
+| `--upstream-remote <name>` | Git remote pointing at the PR target repo (e.g. `upstream`, `origin`). If omitted, detect and prompt.                       |
+| `--base <branch>`          | Base branch the PR merges into (e.g. `master`). If omitted, use the upstream's default branch and prompt to confirm.        |
+| `--merge`                  | Merge upstream base into the feature branch before creating the PR. If omitted, prompt.                                     |
+| `--mode automatic`         | Fixes are applied, committed, pushed, and comments resolved automatically.                                                  |
+| `--mode interactive`       | Fixes are staged; skill pauses before commit/push/resolve so the user can review.                                           |
+| `--pr <number>`            | Monitor and iterate on an existing PR. Skips Steps 1–5 (no merge, no PR creation, no code review). Only `--mode` is needed. |
+
+If `--mode` is not specified, ask the user.
+
+If `--pr` is provided, skip directly to Step 6 (monitor) and Step 7
+(iteration loop). Do not prompt for remote, merge, title, body, reviewers,
+or labels — those only apply when creating a new PR.
+
+## Prerequisites
+
+1. Verify `gh` is installed and authenticated (`gh auth status`). If not,
+   link to https://github.com/cli/cli#installation and stop.
+2. Check if PowerShell is available for dialog notifications. If
+   unavailable, fall back to text-only alerts.
+3. The merge step in Step 2 requires the `babylon-skills:merge-and-resolve`
+   skill. Do **not** try to pre-check its availability — the agent's
+   available skills list may be truncated, which causes false negatives.
+   Always offer the merge option in Step 1a; if invocation in Step 2
+   fails because the skill isn't installed, warn the user and skip.
+
+> ⚠️ **Always pass `--no-pager` to `git`** (e.g. `git --no-pager log`,
+> `git --no-pager diff`, `git --no-pager show`). Without it, commands can
+> launch an interactive pager (`less`) that blocks the shell. This
+> applies to every `git` invocation in this skill, not just the examples
+> shown below.
+
+## Step 1: Gather all inputs up front
+
+> **If `--pr` was provided**, skip this entire step and Steps 2–5. Only
+> collect `--mode` (ask if not specified), then jump to Step 6.
+
+> **Every user prompt in this skill MUST use the `ask_user` tool** — not
+> plain chat text. Provide multiple-choice options where possible (e.g.
+> yes/no, automatic/interactive, detected-remote/other). Ask one question
+> at a time and wait for the answer before proceeding.
+>
+> **If the user replies with freeform feedback** (e.g. "also add reviewer X",
+> "change the title to X"), apply the change and **re-ask the same
+> question** with the updated options. Only continue once the user
+> picks a final option without further changes.
+
+Collect everything before starting the workflow so it doesn't stop midway.
+
+### 1a. Remotes, base branch, and merge
+
+1. Detect git remotes (`git remote -v`).
+2. **Push remote (user's fork)** — the remote whose URL contains the user's
+   GitHub login (`gh api user --jq ".login"`). If `--push-remote` is
+   specified, use it; otherwise present the detected fork and ask the user
+   to confirm or change it.
+3. **Upstream remote (PR target)** — the remote pointing at
+   `BabylonJS/Babylon.js` (often named `upstream` or `origin`). If
+   `--upstream-remote` is specified, use it; otherwise present the
+   detected remote and ask the user to confirm or change it.
+4. **Base branch** — if `--base` is specified, use it; otherwise default
+   to the upstream's default branch
+   (`gh repo view BabylonJS/Babylon.js --json "defaultBranchRef" --jq ".defaultBranchRef.name"`,
+   typically `master`) and prompt the user to confirm.
+5. Once the upstream remote and base branch are confirmed, fetch so the
+   base reference is current:
+   `git fetch <upstream-remote> <base-branch>`.
+6. **If `--merge` not specified**, ask:
+   _"Would you like to merge and resolve before creating the PR?"_
+   The `babylon-skills:merge-and-resolve` skill handles merging the
+   upstream base into the feature branch.
+
+Remember `<push-remote>`, `<upstream-remote>`, `<base-branch>`, and
+`<self-login>` (from `gh api user --jq ".login"`) — they are reused in
+1c, 1d, Step 2, and Step 3.
+
+### 1b. Mode
+
+**If `--mode` not specified**, ask:
+
+- **Automatic** — everything happens without pausing.
+- **Interactive** — pauses at key points so you can review before changes
+  are committed/pushed.
+
+### 1c. PR title and body
+
+1. Analyze **only branch-specific changes** using three-dot diff against
+   `<upstream-remote>/<base-branch>` (resolved in 1a):
+
+    ```bash
+    # Branch commits with full messages (not just --oneline) so you can
+    # read author intent, not just code deltas
+    git --no-pager log <upstream-remote>/<base-branch>...HEAD
+
+    # Files changed by the branch only (excludes merged-in upstream changes)
+    git --no-pager diff <upstream-remote>/<base-branch>...HEAD --stat
+    ```
+
+    > ⚠️ Do **not** use two-dot `..` or compare against local `master` —
+    > either can include unrelated upstream commits or miss recent
+    > upstream work, inflating the file count.
+
+2. Generate a proposed title and body **using both the code diff and
+   the commit messages** — the messages often describe intent,
+   motivation, and linked issues that the diff alone doesn't convey.
+   The body should start with:
+   `> 🤖 *This PR was created by the create-pr skill.*`
+   Include a clear explanation of the changes, motivation, and any
+   behavioral changes. Include links to related PRs or issues if
+   referenced in commit messages.
+3. Present to the user — they can accept, modify, or provide their own.
+
+### 1d. Reviewers
+
+Suggest the top 1–2 upstream-org members who authored or reviewed
+previous PRs touching the files/folders changed by this PR. Do the
+whole pipeline non-interactively. Reuse `<upstream-remote>`,
+`<upstream-owner>`, `<upstream-repo>`, `<base-branch>`, and
+`<self-login>` from Step 1a.
+
+1. **Collect recent commit SHAs** on the base that touched the PR's
+   changed files:
+
+    ```bash
+    git --no-pager diff --name-only <upstream-remote>/<base-branch>...HEAD
+    git --no-pager log <upstream-remote>/<base-branch> --format="%H" -n 30 -- <file1> <file2> ...
+    ```
+
+2. **For each SHA, map to its PR and collect author + review-submitters.**
+   Each appearance = +1 score for that login. Skip commits with no
+   associated PR.
+
+    ```bash
+    gh api "/repos/<upstream-owner>/<upstream-repo>/commits/<sha>/pulls" --jq ".[0].number"
+    gh api "/repos/<upstream-owner>/<upstream-repo>/pulls/<pr>" --jq ".user.login"
+    gh api "/repos/<upstream-owner>/<upstream-repo>/pulls/<pr>/reviews" --jq "[.[].user.login] | unique | .[]"
+    ```
+
+3. **Rank by score** (highest first).
+
+4. **Walk the ranked list and filter.** Drop and continue for:
+    - `<self-login>`
+    - Bots (logins ending in `[bot]`)
+    - Non-members of the upstream org:
+      `gh api "/orgs/<upstream-owner>/members/<login>" --silent` (exit 0 = member).
+      Fallback for user-owned repos:
+      `gh api "/repos/<upstream-owner>/<upstream-repo>/collaborators/<login>" --silent`.
+
+    Stop after the first 1–2 survivors.
+
+5. **Present** the 1–2 candidates. Ask the user to confirm or change.
+   If none survive, skip `--reviewer` on `gh pr create`.
+
+Loop over commits explicitly — don't try to one-line the whole pipeline.
+
+### 1e. Labels
+
+Determine labels from the changed files using the rules in
+[`.github/instructions/pr-labels.md`](../../instructions/pr-labels.md).
+
+Present suggested labels and ask the user to confirm or change.
+
+### 1f. Summary and plan
+
+Present the summary and wait for confirmation:
+
+```
+Here's the plan:
+- Push remote (fork):    <push-remote>
+- Upstream remote:       <upstream-remote>
+- Base branch:           <base-branch>
+- Merge upstream first:  yes / skip
+- Mode:                  automatic / interactive
+- Title:                 <title>
+- Reviewers:             <reviewers>
+- Labels:                <labels>
+
+Steps:
+1. Merge and resolve upstream changes (if selected)
+2. Push branch and create draft PR
+3. Run self code review (code-review skill)
+4. Commit and push code review fixes, mark PR as ready for review
+5. Monitor PR and apply fixes for review comments / CI failures
+
+Ready to proceed?
+```
+
+## Step 2: Merge and resolve (optional)
+
+If the user opted to merge, invoke as a sub-agent, passing the resolved
+base branch and upstream remote from Step 1a:
+
+```
+/babylon-skills:merge-and-resolve <base-branch> <upstream-remote> --mode <automatic|interactive>
+```
+
+If invocation fails because the skill is not installed, warn the user
+_"The babylon-skills:merge-and-resolve skill was not found — skipping
+merge step."_ and continue.
+
+## Step 3: Create the draft PR
+
+Use `<push-remote>`, `<upstream-remote>`, and `<base-branch>` from 1a.
+
+1. Push the branch:
+
+    ```bash
+    git push -u <push-remote> HEAD
+    ```
+
+2. Get the current branch name and user login:
+
+    ```bash
+    git rev-parse --abbrev-ref HEAD
+    gh api user --jq ".login"
+    ```
+
+3. Determine the upstream owner/repo from the upstream remote URL (e.g.
+   `git remote get-url <upstream-remote>` → parse `owner/repo`). For this
+   repo that is `BabylonJS/Babylon.js`.
+
+4. Create the draft PR. Write the title and body to temp files first
+   so shell escaping doesn't mangle backticks, `$`, `!`, or backslashes
+   in the markdown, then pass the single-line title with
+   `--title "$(cat ...)"` and the multi-line body with `--body-file`:
+
+    ```bash
+    # Write files (exact markdown, no escaping needed)
+    # ... create pr-title.txt and pr-body.md ...
+
+    gh pr create \
+      --repo "<upstream-owner>/<upstream-repo>" \
+      --head "<user>:<branch>" \
+      --base "<base-branch>" \
+      --title "$(cat pr-title.txt)" \
+      --body-file pr-body.md \
+      --draft \
+      --label "<label>" \
+      --reviewer "<reviewer>"
+
+    rm pr-title.txt pr-body.md
+    ```
+
+    > `gh pr create` does not accept `--title-file`, so a short
+    > single-line title via `$(cat ...)` is fine; the multi-line body
+    > must use `--body-file`.
+
+    > `--label` and `--reviewer` can each be repeated (or take a
+    > comma-separated list) — pass one flag per label/reviewer chosen
+    > in 1d/1e.
+
+5. `gh pr create` prints the new PR's full URL on success — surface it
+   prominently in the chat (e.g. _"Draft PR created: <url>"_) so the
+   user can click through to review it.
+
+## Step 4: Self code review
+
+1. Invoke the code-review skill, passing through the mode:
+
+    ```
+    /code-review --mode <automatic|interactive>
+    ```
+
+2. **If interactive:** pause after code-review completes and ask the user
+   to review the changes before committing.
+
+3. If code-review produced changes, commit:
+
+    ```
+    Code review fixes (automated by code-review skill)
+
+    Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
+    ```
+
+4. Push: `git push <push-remote> HEAD`
+
+## Step 5: Mark PR as ready for review
+
+1. Mark ready:
+
+    ```bash
+    gh pr ready <pr-number> --repo "<upstream-owner>/<upstream-repo>"
+    ```
+
+2. Add a PR comment. If code-review produced changes, link to the commit
+   and list the fixes as a bullet list on the next line:
+
+    ```
+    Self code review completed by the code-review skill. Review fixes: https://github.com/<owner>/<repo>/pull/<pr-number>/changes/<commit-sha>
+    - <fix 1 — brief description>
+    - <fix 2 — brief description>
+    ```
+
+    If no changes: _"Self code review completed by the code-review skill. No issues found."_
+
+    > ⚠️ Post the comment with `--body-file`, never with `--body`.
+    > Shells interpret backticks, `$`, `!`, and backslashes inside
+    > double-quoted strings, which mangles markdown code spans and
+    > special characters. Write the comment body to a temp file (e.g.
+    > `pr-comment.md`) exactly as it should appear, then:
+    >
+    > ```bash
+    > gh pr comment <pr-number> --repo "<upstream-owner>/<upstream-repo>" --body-file pr-comment.md
+    > rm pr-comment.md
+    > ```
+
+## Step 6: Monitor the PR
+
+Invoke the monitor-pr skill with the PR number (either from Step 3 or
+from the `--pr` argument):
+
+```
+/monitor-pr <pr-number>
+```
+
+monitor-pr does not accept a `--mode` argument — it just polls and prints
+status. The iteration loop below (Step 7) is what handles fixes in the
+mode chosen back in Step 1b.
+
+## Step 7: Iteration loop
+
+Watch the monitor-pr output and react to actionable events.
+
+### Handling events
+
+1. **Unresolved review comments:** Enumerate them with a single
+   GraphQL query that captures everything you need to react, reply, and
+   resolve (so you don't re-query later):
+
+    ```bash
+    gh api graphql -f query='
+    query {
+      repository(owner: "<owner>", name: "<repo>") {
+        pullRequest(number: <pr-number>) {
+          reviewThreads(first: 100) {
+            nodes {
+              id                 # thread id (PRRT_...) — used to resolve the thread
+              isResolved
+              isOutdated
+              path
+              line
+              comments(first: 5) {
+                nodes {
+                  databaseId     # numeric id — used to reply to the comment
+                  author { login }
+                  body
+                  url            # also encodes the databaseId as #discussion_r<databaseId>
+                }
+              }
+            }
+          }
+        }
+      }
+    }'
+    ```
+
+    For each unresolved thread, read the comment, analyze if it needs a
+    code change and/or response. Make fixes. Prepare a response prefixed
+    with `[Responded by Copilot on behalf of <user>]` (user from
+    `gh api user --jq ".login"`). Carry the thread `id` and parent
+    comment `databaseId` forward — they're needed when posting the
+    reply and resolving the thread.
+
+2. **Pipeline/CI failures (real, not flakes):** Read CI logs, identify root
+   cause, make the fix.
+
+3. **Test failures:** Same as pipeline failures — fix the code, not the
+   test (unless the test is wrong).
+
+### After making fixes
+
+**Always run the Quality commands from `.github/copilot-instructions.md`
+before pushing**, plus any tests relevant to the changed code (e.g.
+integration/visualization tests for rendering changes). Iterate until
+they pass — do not push broken code.
+
+**Interactive mode** — gate on user approval first:
+
+1. Stage changes: `git add -A`
+2. **Do NOT commit, push, respond, or resolve yet.**
+3. Present separate tables for each category (only include tables that
+   apply):
+
+    **Review comment fixes:**
+
+    | #   | Comment                             | Proposed Response | Code Changes                |
+    | --- | ----------------------------------- | ----------------- | --------------------------- |
+    | 1   | [`<comment text>`](link-to-comment) | `<response>`      | `<fix description + files>` |
+
+    Keep the table compact — it's for the human to review. Persist the
+    thread `id` and parent comment `databaseId` for each row in
+    session-local storage (e.g. a `review_threads` SQL table keyed by
+    row `#`) so the reply/resolve step can look them up without
+    re-querying or cluttering the table.
+
+    **Pipeline failure fixes:**
+
+    | #   | Pipeline Failure                      | Code Changes                |
+    | --- | ------------------------------------- | --------------------------- |
+    | 1   | [`<job — error>`](link-to-failed-run) | `<fix description + files>` |
+
+    **Test failure fixes:**
+
+    | #   | Test Failure                         | Code Changes                |
+    | --- | ------------------------------------ | --------------------------- |
+    | 1   | [`<test — error>`](link-to-test-log) | `<fix description + files>` |
+
+4. Show a dialog (if PowerShell available):
+    ```
+    powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Fixes are staged and ready for review.', 'Fixes Ready', 'OK', 'Information')"
+    ```
+5. Wait for user approval, then proceed with the Automatic mode steps
+   below.
+
+**Automatic mode:** Commit (new commit, never amend), push, respond to
+comments, resolve threads (see "Posting responses to review comments"
+below for how to reply correctly). The monitor picks up new checks
+automatically.
+
+### Posting responses to review comments
+
+When responding (in either mode), **post the response as a reply to the
+review comment, not a top-level PR comment.** Do **not** use
+`gh pr comment` — it creates an unlinked PR-level comment.
+
+Use the parent `databaseId` and thread `id` persisted for this row in
+session-local storage (populated from the GraphQL query at the top of
+Step 7). Do **not** re-query — the IDs are already in hand. As a
+fallback, the parent `databaseId` is also encoded in the comment's URL
+as `#discussion_r<databaseId>`.
+
+Post the reply via REST:
+
+```bash
+gh api -X POST \
+  "/repos/<owner>/<repo>/pulls/<pr-number>/comments/<parent-id>/replies" \
+  -F body=@reply.md
+rm reply.md
+```
+
+Then resolve the thread via the `resolveReviewThread` GraphQL mutation
+using the captured thread `id`.
+
+### Exit conditions
+
+- All checks pass, PR approved, all comments resolved → monitor-pr handles
+  the "ready to merge" notification.
+- User explicitly asks to stop.
+- Same issue fails 3 times → stop and ask the user for help.
+
+## Guidelines
+
+- **Never force push.** Never amend previous commits. Always create new
+  commits.
+- **Always use the user's fork.** Never push to upstream org repos.
+- **Never merge without explicit user approval.**
+- **Prefix review responses** with `[Responded by Copilot on behalf of <user>]`.
+- **Keep PRs focused.** Don't mix fixes with refactors.
+- **Update PR descriptions** when the approach changes.
+- **`gh pr merge --auto`** merges immediately if the repo has no branch
+  protection — ask before using it.
diff --git a/.github/skills/monitor-pr/SKILL.md b/.github/skills/monitor-pr/SKILL.md
@@ -0,0 +1,227 @@
+---
+name: monitor-pr
+description: |
+    Monitor one or more GitHub PRs and maintain a live status table showing
+    title, link, check status, resolved/total comments, and reviewer approval.
+    Shows a Windows dialog when a PR is ready to merge.
+    Input: a comma-separated list of PR numbers, "mine", or "all".
+argument-hint: <pr-numbers | mine | all>
+---
+
+# Monitor PR
+
+Poll GitHub PRs and print a live status table to the main chat. Alert when
+a PR is ready to merge.
+
+## Input
+
+Parse `$ARGUMENTS`:
+
+| Value                                      | Meaning                                   |
+| ------------------------------------------ | ----------------------------------------- |
+| Comma-separated numbers (e.g. `1234,5678`) | Monitor those specific PRs                |
+| `mine`                                     | All open PRs authored by the current user |
+| `all`                                      | All open PRs in the repo                  |
+
+If `$ARGUMENTS` is empty, use the `ask_user` tool (not plain chat text)
+to prompt the user with choices: `mine`, `all`, or a freeform list of PR
+numbers. Do not proceed until the user has answered.
+
+## Prerequisites
+
+1. Verify `gh` is installed and authenticated (`gh auth status`). If not,
+   link to https://github.com/cli/cli#installation and stop.
+2. Check if PowerShell is available (`powershell -Command "echo ok"`). If
+   unavailable, skip dialog notifications and use text-only alerts.
+
+## Step 1: Resolve the PR list
+
+```bash
+# Specific PRs — validate each exists
+gh pr view <number> --repo "BabylonJS/Babylon.js" --json "number"
+
+# "mine"
+gh pr list --repo "BabylonJS/Babylon.js" -A "@me" --json "number,title,url"
+
+# "all" (defaults to open)
+gh pr list --repo "BabylonJS/Babylon.js" --json "number,title,url"
+```
+
+## Step 2: Build and display the status table
+
+For each PR, gather the following data (this table **describes the
+columns** — it is not the output format):
+
+| Column   | Source                                                                                                                                     |
+| -------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
+| PR       | `#<number>` linked to the PR URL                                                                                                           |
+| Title    | `gh pr view --json "title"`                                                                                                                |
+| Checks   | `gh pr view --json "statusCheckRollup"` — ✅ `all pass` / ❌ `N fail, M pending (ETA ~Xm)` / ⏳ `N pending (ETA ~Xm)`. See ETA note below. |
+| Comments | GraphQL `reviewThreads` query — ✅ `all resolved` / ❌ `N/M resolved`                                                                      |
+| Approved | `gh pr view --json "reviewDecision"` — ✅ `approved` / ❌ `not approved` (the field is an enum, not a count)                              |
+| Ready    | ✅ `ready` if all checks pass AND approved AND all comments resolved, ❌ `not ready` otherwise                                             |
+
+Review threads require the GraphQL API since `gh pr view --json` does not
+expose them:
+
+```bash
+gh api graphql -f query='
+query {
+  repository(owner: "BabylonJS", name: "Babylon.js") {
+    pullRequest(number: <NUMBER>) {
+      reviewThreads(first: 100) {
+        totalCount
+        nodes { isResolved }
+      }
+    }
+  }
+}' --jq '.data.repository.pullRequest.reviewThreads | {total: .totalCount, resolved: ([.nodes[] | select(.isResolved)] | length)}'
+```
+
+> If `totalCount > 100`, the single-page query above will undercount
+> resolved threads. Page through with `pageInfo { hasNextPage endCursor }`
+> + `after:` until all threads are fetched, then sum the resolved counts.
+
+### Checks ETA
+
+When any checks are still running, compute a rough ETA **before** rendering
+the table. The Checks cell is incomplete without it.
+
+1. For each **in-progress** check (`status != COMPLETED`):
+    - `elapsed = now - startedAt` (from `statusCheckRollup`).
+    - Look up a **historical duration** for the same check name from
+      the most recent merged PR that ran it:
+        ```bash
+        gh pr list --repo "<owner>/<repo>" -s merged -L 5 --json "number"
+        gh pr view <recent-pr> --repo "<owner>/<repo>" --json "statusCheckRollup" \
+          --jq '.statusCheckRollup[] | select(.name == "<name>" and .status == "COMPLETED") | {startedAt, completedAt}'
+        ```
+        `historical = completedAt - startedAt`.
+    - `remaining = max(historical - elapsed, 1m)`. If no history, use
+      `elapsed` as a lower bound and mark ETA as `~Xm+`.
+2. For each **queued / not-started** check (`status == QUEUED` or
+   missing `startedAt`): `remaining = historical` (full duration).
+3. Checks run in **parallel**, so the overall PR ETA is
+   `max(remaining)` across all pending checks — not the sum.
+4. Round to whole minutes. If the computed ETA is negative or < 1m,
+   show `<1m`.
+
+Cache historical durations per check name across PRs within a single
+poll iteration to avoid redundant `gh` calls. **Do not** cache across
+polls (stale data risk — see the polling rule below).
+
+### Output format
+
+Only render the table **after** all per-PR data (including ETA) is
+gathered. Every pending-checks cell MUST end with `(ETA ~Xm)` (or
+`~Xm+` / `<1m`) — no ETA means the data isn't ready yet.
+
+Render as a **markdown table, one row per PR**, with the columns above
+as headers in the same order. Do not transpose or split into per-PR
+tables. Prefix with a header line showing the OS's **local** time, e.g.
+`PR Status — 2026-04-17 05:17 PM PDT` (`date` or `Get-Date`).
+
+Example:
+
+| PR                        | Title   | Checks                 | Comments              | Approved        | Ready        |
+| ------------------------- | ------- | ---------------------- | --------------------- | --------------- | ------------ |
+| [#1234](https://.../1234) | Fix foo | ⏳ 2 pending (ETA ~5m) | ✅ all resolved (4/4) | ❌ not approved | ❌ not ready |
+| [#5678](https://.../5678) | Add bar | ✅ all pass            | ✅ all resolved       | ✅ 1 approval   | ✅ ready     |
+
+## Step 3: Distinguish real failures from flakes
+
+When checks fail, read the CI logs. Source depends on which CI the
+check is on — look at `statusCheckRollup[].detailsUrl` to tell:
+
+- **GitHub Actions** (`detailsUrl` on `github.com`) — use GitHub MCP
+  `get_job_logs`, or `gh run view <run-id> --log-failed`.
+- **Azure DevOps Pipelines** (`detailsUrl` on `dev.azure.com`) — the
+  Babylon.js ADO org (`babylonjs`) allows **anonymous** API access;
+  no auth needed. The `detailsUrl` looks like
+  `https://dev.azure.com/<org>/<project-guid>/_build/results?buildId=<id>&view=logs&jobId=<job-guid>`.
+  Fetch the build timeline and then the failing record's log:
+
+    ```bash
+    # List all records (jobs/tasks) and their log URLs
+    curl -s "https://dev.azure.com/<org>/<project-guid>/_apis/build/builds/<buildId>/timeline?api-version=7.0"
+
+    # Fetch a specific record's log
+    curl -s "<record.log.url>"
+    ```
+
+    Filter `timeline.records` to the failing entries (`result == "failed"`)
+    and read each `.log.url`. If a `jobId` is present in `detailsUrl`,
+    scope directly to that record's children.
+
+Classification:
+
+- **Real failure** — caused by changes in the PR. Show ❌ with a brief
+  error summary.
+- **Flake** — a test that failed on some iterations and passed on others,
+  and is not a new test added in the PR. Show ⚠️ and note it as a
+  suspected flake.
+
+## Step 4: Poll loop
+
+> **MANDATORY: You MUST implement a continuous polling loop.** Do not
+> display the status once and stop. Do not suggest the user re-invoke the
+> skill to refresh. You must keep running and re-checking every ~5 minutes
+> until every monitored PR is merged or closed. Use `sleep 300` (or
+> equivalent) between polls to wait 5 minutes, then re-fetch and print
+> the updated table. This is the core purpose of this skill.
+
+### How to poll
+
+1. After printing the initial status table, sleep for 5 minutes:
+    ```bash
+    sleep 300
+    ```
+2. After sleeping, **re-fetch ALL PR data from scratch** using the same
+   `gh` and GraphQL commands as Step 2. Every column — checks, comments,
+   approval, state — must be queried fresh from the API. **Do not reuse
+   or cache any data from a previous polling iteration.** New commits
+   can restart all checks, so data from a previous poll may be stale.
+3. Print the fully refreshed status table to the main chat.
+4. Repeat from step 1.
+
+### On each poll, also check
+
+- If a PR becomes **ready to merge** (all checks pass, approved, all
+  comments resolved):
+    - Show a Windows dialog (if PowerShell is available):
+        ```
+        powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('PR #<number> — <title> — is ready to merge.', 'PR Ready', 'OK', 'Information')"
+        ```
+    - Always also print a prominent message in the chat.
+- If a PR is merged or closed, remove it from the table and note it.
+
+### When to stop
+
+Stop polling **only** when:
+
+- Every monitored PR has been merged or closed, OR
+- The user explicitly tells you to stop.
+
+**Do NOT stop for any other reason.** Do not stop because "polling isn't
+practical in a chat session." Do not stop because "the user can re-invoke
+the skill." The entire point of this skill is continuous, autonomous
+monitoring.
+
+## Retriggering CI
+
+If the user asks to retrigger CI (e.g. for flakes), push an empty commit:
+
+```bash
+git commit --allow-empty -m "retrigger CI"
+git push
+```
+
+**Never force push.** Always use new commits.
+
+## Guidelines
+
+- Always read CI logs on failures — don't guess at the cause.
+- Print the status table to the main chat so the user can follow along.
+- **You MUST keep polling until all PRs are merged/closed or the user
+  tells you to stop.** Do not exit early. Do not suggest the user
+  re-invoke the skill. This skill runs continuously.
PATCH

echo "Gold patch applied."
