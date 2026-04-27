#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "- **Describe the net result, not the journey**: The description covers the end s" "plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md b/plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md
@@ -5,19 +5,21 @@ description: Commit, push, and open a PR with an adaptive, value-first descripti
 
 # Git Commit, Push, and PR
 
-Go from working tree changes to an open pull request in a single workflow, or update an existing PR description. The key differentiator of this skill is PR descriptions that communicate *value and intent* proportional to the complexity of the change.
+Go from working changes to an open pull request, or rewrite an existing PR description.
+
+**Asking the user:** When this skill says "ask the user", use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If unavailable, present the question and wait for a reply.
 
 ## Mode detection
 
-If the user is asking to update, refresh, or rewrite an existing PR description (with no mention of committing or pushing), this is a **description-only update**. The user may also provide a focus for the update (e.g., "update the PR description and add the benchmarking results"). Note any focus instructions for use in DU-3.
+If the user is asking to update, refresh, or rewrite an existing PR description (with no mention of committing or pushing), this is a **description-only update**. The user may also provide a focus (e.g., "update the PR description and add the benchmarking results"). Note any focus for DU-3.
 
 For description-only updates, follow the Description Update workflow below. Otherwise, follow the full workflow.
 
 ## Context
 
 **If you are not Claude Code**, skip to the "Context fallback" section below and run the command there to gather context.
 
-**If you are Claude Code**, the six labeled sections below (Git status, Working tree diff, Current branch, Recent commits, Remote default branch, Existing PR check) contain pre-populated data. Use them directly throughout this skill -- do not re-run these commands.
+**If you are Claude Code**, the six labeled sections below contain pre-populated data. Use them directly -- do not re-run these commands.
 
 **Git status:**
 !`git status`
@@ -53,15 +55,11 @@ printf '=== STATUS ===\n'; git status; printf '\n=== DIFF ===\n'; git diff HEAD;
 
 ### DU-1: Confirm intent
 
-Ask the user to confirm: "Update the PR description for this branch?" Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the question and wait for the user's reply.
-
-If the user declines, stop.
+Ask the user: "Update the PR description for this branch?" If declined, stop.
 
 ### DU-2: Find the PR
 
-Use the current branch and existing PR check from the context above. If the current branch is empty (detached HEAD), report that there is no branch to update and stop.
-
-If the existing PR check returned JSON with `state: OPEN`, an open PR exists — proceed to DU-3. Otherwise (`NO_OPEN_PR` or a non-OPEN state), report no open PR and stop.
+Use the current branch and existing PR check from context. If the current branch is empty (detached HEAD), report no branch and stop. If the PR check returned `state: OPEN`, proceed to DU-3. Otherwise, report no open PR and stop.
 
 ### DU-3: Write and apply the updated description
 
@@ -71,16 +69,16 @@ Read the current PR description:
 gh pr view --json body --jq '.body'
 ```
 
-Build the updated description in this order:
+Build the updated description:
 
-1. **Get the full branch diff** -- follow "Detect the base branch and remote" and "Gather the branch scope" in Step 6. Use the PR found in DU-2 as the existing PR for base branch detection.
-2. **Classify commits** -- follow "Classify commits before writing" in Step 6. This matters especially for description updates, where the recent commits that prompted the update are often fix-up work (code review fixes, lint fixes) rather than feature work.
-3. **Decide on evidence** -- check if the current PR description already contains evidence (a `## Demo` or `## Screenshots` section with image embeds). If evidence exists, preserve it unless the user's focus specifically asks to refresh or remove it. If no evidence exists, follow "Evidence for PR descriptions" in Step 6. Description-only updates may be specifically intended to add evidence.
-4. **Write the new description** -- follow the writing principles in Step 6, driven by feature commits, final diff, and evidence decision.
+1. **Get the full branch diff** -- follow "Detect the base branch and remote" and "Gather the branch scope" in Step 6. Use the PR found in DU-2 for base branch detection.
+2. **Classify commits** -- follow "Classify commits before writing" in Step 6.
+3. **Decide on evidence** -- if the current description already has a `## Demo` or `## Screenshots` section with image embeds, preserve it unless the user's focus asks to refresh or remove it. If no evidence exists, follow "Evidence for PR descriptions" in Step 6.
+4. **Rewrite the description from scratch** -- follow the writing principles in Step 6, driven by feature commits, final diff, and evidence decision. Do not layer changes onto the old description or document what changed since the last version. Write as if describing the PR for the first time.
    - If the user provided a focus, incorporate it alongside the branch diff context.
-5. **Compare and confirm** -- summarize the substantial changes vs the current description (e.g., "Added coverage of the new caching layer, updated test plan, removed outdated migration notes").
+5. **Compare and confirm** -- briefly explain what the new description covers differently from the old one. This helps the user decide whether to apply; the description itself does not narrate these differences.
    - If the user provided a focus, confirm it was addressed.
-   - Ask the user to confirm before applying. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the summary and wait for the user's reply.
+   - Ask the user to confirm before applying.
 
 If confirmed, apply:
 
@@ -99,62 +97,53 @@ Report the PR URL.
 
 ### Step 1: Gather context
 
-Use the context above (git status, working tree diff, current branch, recent commits, remote default branch, and existing PR check). All data needed for this step and Step 3 is already available -- do not re-run those commands.
+Use the context above. All data needed for this step and Step 3 is already available -- do not re-run those commands.
 
-The remote default branch value returns something like `origin/main`. Strip the `origin/` prefix to get the branch name. If it returned `DEFAULT_BRANCH_UNRESOLVED` or a bare `HEAD`, try:
+The remote default branch value returns something like `origin/main`. Strip the `origin/` prefix. If it returned `DEFAULT_BRANCH_UNRESOLVED` or a bare `HEAD`, try:
 
 ```bash
 gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
 ```
 
 If both fail, fall back to `main`.
 
-If the current branch from the context above is empty, the repository is in detached HEAD state. Explain that a branch is required before committing and pushing. Ask whether to create a feature branch now. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply.
-
-- If the user agrees, derive a descriptive branch name from the change content, create it with `git checkout -b <branch-name>`, then run `git branch --show-current` again and use that result as the current branch name for the rest of the workflow.
-- If the user declines, stop.
+If the current branch is empty (detached HEAD), explain that a branch is required. Ask whether to create a feature branch now.
+- If yes, derive a branch name from the change content, create with `git checkout -b <branch-name>`, and use that for the rest of the workflow.
+- If no, stop.
 
-If the git status from the context above shows a clean working tree (no staged, modified, or untracked files), determine the next action based on upstream state and PR status. The current branch and existing PR check are already available from the context above. Additionally:
+If the working tree is clean (no staged, modified, or untracked files), determine the next action:
 
-1. Run `git rev-parse --abbrev-ref --symbolic-full-name @{u}` to check whether an upstream is configured.
-2. If the command succeeds, run `git log <upstream>..HEAD --oneline` using the upstream name from the previous command.
+1. Run `git rev-parse --abbrev-ref --symbolic-full-name @{u}` to check upstream.
+2. If upstream exists, run `git log <upstream>..HEAD --oneline` for unpushed commits.
 
-Then follow this decision tree:
+Decision tree:
 
-- **On default branch** (`main`, `master`, or the resolved default branch) with no upstream or unpushed commits:
-  - Ask whether to create a feature branch first (pushing the default branch directly is not supported by this workflow). Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply.
-  - If yes -> create branch with `git checkout -b <branch-name>`, continue from Step 5 (push)
-  - If no -> stop
-- **On default branch**, all commits pushed, no open PR:
-  - Report there is no feature branch work to open as a PR. Stop.
-- **No upstream configured** (feature branch, never pushed):
-  - Skip Step 4 (commit), continue from Step 5 (push)
-- **Unpushed commits exist** (feature branch, upstream configured):
-  - Skip Step 4 (commit), continue from Step 5 (push)
-- **All commits pushed, no open PR** (feature branch):
-  - Skip Steps 4-5, continue from Step 6 (PR description) and Step 7 (create PR)
-- **All commits pushed, open PR exists**:
-  - Report that everything is up to date. Stop.
+- **On default branch, unpushed commits or no upstream** -- ask whether to create a feature branch (pushing default directly is not supported). If yes, create and continue from Step 5. If no, stop.
+- **On default branch, all pushed, no open PR** -- report no feature branch work. Stop.
+- **Feature branch, no upstream** -- skip Step 4, continue from Step 5.
+- **Feature branch, unpushed commits** -- skip Step 4, continue from Step 5.
+- **Feature branch, all pushed, no open PR** -- skip Steps 4-5, continue from Step 6.
+- **Feature branch, all pushed, open PR** -- report up to date. Stop.
 
 ### Step 2: Determine conventions
 
-Follow this priority order for commit messages *and* PR titles:
+Priority order for commit messages and PR titles:
 
-1. **Repo conventions already in context** -- If project instructions (AGENTS.md, CLAUDE.md, or similar) are loaded and specify conventions, follow those. Do not re-read these files; they are loaded at session start.
-2. **Recent commit history** -- If no explicit convention exists, match the pattern visible in the last 10 commits.
-3. **Default: conventional commits** -- `type(scope): description` as the fallback.
+1. **Repo conventions in context** -- follow project instructions if they specify conventions. Do not re-read; they load at session start.
+2. **Recent commit history** -- match the pattern in the last 10 commits.
+3. **Default** -- `type(scope): description` (conventional commits).
 
 ### Step 3: Check for existing PR
 
-Use the current branch and existing PR check from the context above. If the current branch is empty, report that the workflow is in detached HEAD state and stop.
+Use the current branch and existing PR check from context. If the branch is empty, report detached HEAD and stop.
 
-If the existing PR check returned JSON with `state: OPEN`, note the URL — continue to Step 4 and Step 5, then skip to Step 7 (existing PR flow). Otherwise (`NO_OPEN_PR` or a non-OPEN state), continue to Step 4 through Step 8.
+If the PR check returned `state: OPEN`, note the URL -- continue to Step 4 and 5, then skip to Step 7 (existing PR flow). Otherwise, continue through Step 8.
 
 ### Step 4: Branch, stage, and commit
 
-1. If the current branch from the context above is `main`, `master`, or the resolved default branch from Step 1, create a descriptive feature branch first with `git checkout -b <branch-name>`. Derive the branch name from the change content.
-2. Before staging everything together, scan the changed files for naturally distinct concerns. If modified files clearly group into separate logical changes (e.g., a refactor in one set of files and a new feature in another), create separate commits for each group. Keep this lightweight -- group at the **file level only** (no `git add -p`), split only when obvious, and aim for two or three logical commits at most. If it's ambiguous, one commit is fine.
-3. For each commit group, stage and commit in a single call. Avoid `git add -A` or `git add .` to prevent accidentally including sensitive files. Follow the conventions from Step 2. Use a heredoc for the message:
+1. If on the default branch, create a feature branch first with `git checkout -b <branch-name>`.
+2. Scan changed files for naturally distinct concerns. If files clearly group into separate logical changes, create separate commits (2-3 max). Group at the file level only (no `git add -p`). When ambiguous, one commit is fine.
+3. Stage and commit each group in a single call. Avoid `git add -A` or `git add .`. Follow conventions from Step 2:
    ```bash
    git add file1 file2 file3 && git commit -m "$(cat <<'EOF'
    commit message here
@@ -170,208 +159,161 @@ git push -u origin HEAD
 
 ### Step 6: Write the PR description
 
-Before writing, determine the **base branch** and gather the **full branch scope**. The working-tree diff from Step 1 only shows uncommitted changes at invocation time -- the PR description must cover **all commits** that will appear in the PR.
+The working-tree diff from Step 1 only shows uncommitted changes at invocation time. The PR description must cover **all commits** in the PR.
 
 #### Detect the base branch and remote
 
-Resolve the base branch **and** the remote that hosts it. In fork-based PRs the base repository may correspond to a remote other than `origin` (commonly `upstream`).
+Resolve both the base branch and the remote (fork-based PRs may use a remote other than `origin`). Stop at the first that succeeds:
 
-Use this fallback chain. Stop at the first that succeeds:
-
-1. **PR metadata** (if an existing PR was found in Step 3):
+1. **PR metadata** (if existing PR found in Step 3):
    ```bash
    gh pr view --json baseRefName,url
    ```
-   Extract `baseRefName` as the base branch name. The PR URL contains the base repository (`https://github.com/<owner>/<repo>/pull/...`). Determine which local remote corresponds to that repository:
-   ```bash
-   git remote -v
-   ```
-   Match the `owner/repo` from the PR URL against the fetch URLs. Use the matching remote as the base remote. If no remote matches, fall back to `origin`.
-2. **Remote default branch from context above:** If the remote default branch resolved (not `DEFAULT_BRANCH_UNRESOLVED`), strip the `origin/` prefix and use that. Use `origin` as the base remote.
-3. **GitHub default branch metadata:**
+   Extract `baseRefName`. Match `owner/repo` from the PR URL against `git remote -v` fetch URLs to find the base remote. Fall back to `origin`.
+2. **Remote default branch from context** -- if resolved, strip `origin/` prefix. Use `origin`.
+3. **GitHub metadata:**
    ```bash
    gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
    ```
-   Use `origin` as the base remote.
-4. **Common branch names** -- check `main`, `master`, `develop`, `trunk` in order. Use the first that exists on the remote:
+   Use `origin`.
+4. **Common names** -- check `main`, `master`, `develop`, `trunk` in order:
    ```bash
    git rev-parse --verify origin/<candidate>
    ```
-   Use `origin` as the base remote.
+   Use `origin`.
 
-If none resolve, ask the user to specify the target branch. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply.
+If none resolve, ask the user to specify the target branch.
 
 #### Gather the branch scope
 
-Once the base branch and remote are known, gather the full scope in as few calls as possible.
-
-First, verify the remote-tracking ref exists and fetch if needed:
+Verify the remote-tracking ref exists and fetch if needed:
 
 ```bash
 git rev-parse --verify <base-remote>/<base-branch> 2>/dev/null || git fetch --no-tags <base-remote> <base-branch>
 ```
 
-Then gather the merge base, commit list, and full diff in a single call:
+Gather merge base, commit list, and full diff in a single call:
 
 ```bash
 MERGE_BASE=$(git merge-base <base-remote>/<base-branch> HEAD) && echo "MERGE_BASE=$MERGE_BASE" && echo '=== COMMITS ===' && git log --oneline $MERGE_BASE..HEAD && echo '=== DIFF ===' && git diff $MERGE_BASE...HEAD
 ```
 
-Use the full branch diff and commit list as the basis for the PR description -- not the working-tree diff from Step 1.
+Use the full branch diff and commit list as the basis for the description.
 
 #### Evidence for PR descriptions
 
-Decide whether evidence capture is possible from the full branch diff before writing the PR description.
-
-**Evidence is possible** when the final diff changes observable product behavior that can be demonstrated from the workspace: UI rendering or interactions, CLI commands and output, API/library behavior with runnable example code, generated artifacts, or workflow behavior with visible output.
+Decide whether evidence capture is possible from the full branch diff.
 
-**Evidence is not possible** for docs-only, markdown-only, changelog-only, release metadata, CI/config-only, test-only, or pure internal refactors with no observable output change. It is also not possible when the behavior requires unavailable credentials, paid/cloud services, bot tokens, deploy-only infrastructure, or hardware the user has not provided. In those cases, do not ask about capturing evidence; omit the evidence section and, if relevant, mention the skip reason in the final user report.
+**Evidence is possible** when the diff changes observable behavior demonstrable from the workspace: UI, CLI output, API behavior with runnable code, generated artifacts, or workflow output.
 
-When evidence is possible, ask whether to include it in the PR description. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the options and wait for the user's reply.
+**Evidence is not possible** for:
+- Docs-only, markdown-only, changelog-only, release metadata, CI/config-only, test-only, or pure internal refactors
+- Behavior requiring unavailable credentials, paid/cloud services, bot tokens, deploy-only infrastructure, or hardware not provided
 
-**Question:** "This PR has observable behavior. Capture evidence for the PR description?"
+When not possible, skip without asking. When possible, ask: "This PR has observable behavior. Capture evidence for the PR description?"
 
-**Options:**
-1. **Capture evidence now**: load the `ce-demo-reel` skill with a target description as the argument (e.g., "the new settings page" or "CLI output of the migrate command"). Infer the target from the branch diff. ce-demo-reel returns `Tier`, `Description`, and `URL`. Use the URL and description to build a `## Demo` or `## Screenshots` section (browser-reel/terminal-recording/screenshot-reel use "Demo", static uses "Screenshots").
-2. **Use existing evidence**: ask the user for the URL or markdown embed, then include it in the PR body.
-3. **Skip evidence**: write the PR description without an evidence section.
+1. **Capture now** -- load the `ce-demo-reel` skill with a target description inferred from the branch diff. ce-demo-reel returns `Tier`, `Description`, and `URL`. Build a `## Demo` or `## Screenshots` section (browser-reel/terminal-recording/screenshot-reel use "Demo", static uses "Screenshots").
+2. **Use existing evidence** -- ask for the URL or markdown embed.
+3. **Skip** -- no evidence section.
 
-If the user chooses capture, check ce-demo-reel's output for failure: `Tier: skipped` or `URL: "none"` means no evidence was captured. Do not add a placeholder section. Summarize the skip reason in the final user report.
+If capture returns `Tier: skipped` or `URL: "none"`, do not add a placeholder. Summarize in the final report.
 
-Place the evidence embed before the Compound Engineering badge, typically after the summary or within the changes section. Do not label test output as "Demo" or "Screenshots".
+Place evidence before the Compound Engineering badge. Do not label test output as "Demo" or "Screenshots".
 
 #### Classify commits before writing
 
-Before writing the description, scan the commit list and classify each commit:
+Scan the commit list and classify each commit:
 
-- **Feature commits** -- implement the purpose of the PR (new functionality, intentional refactors, design changes). These drive the description.
-- **Fix-up commits** -- work product of getting the branch ready: code review fixes, lint/type error fixes, test fixes, rebase conflict resolutions, style cleanups, typo corrections in the new code. These are invisible to the reader.
+- **Feature commits** -- implement the PR's purpose (new functionality, intentional refactors, design changes). These drive the description.
+- **Fix-up commits** -- iteration work (code review fixes, lint fixes, test fixes, rebase resolutions, style cleanups). Invisible to the reader.
 
-Only feature commits inform the description. Fix-up commits are noise -- they describe the iteration process, not the end result. The full diff already includes whatever the fix-up commits changed, so their intent is captured without narrating them. When sizing and writing the description, mentally subtract fix-up commits: a branch with 12 commits but 9 fix-ups is a 3-commit PR in terms of description weight.
+When sizing the description, mentally subtract fix-up commits: a branch with 12 commits but 9 fix-ups is a 3-commit PR.
 
 #### Frame the narrative before sizing
 
-After classifying commits, articulate the PR's narrative frame:
+Articulate the PR's narrative frame:
 
 1. **Before**: What was broken, limited, or impossible? (One sentence.)
 2. **After**: What's now possible or improved? (One sentence.)
-3. **Scope rationale** (only if the PR touches 2+ separable-looking concerns): Why do these ship together? (One sentence.)
+3. **Scope rationale** (only if 2+ separable-looking concerns): Why do these ship together? (One sentence.)
 
-This frame becomes the opening of the description. For small+simple PRs (the sizing table routes to 1-2 sentences), the "after" sentence alone may be the entire description -- that's fine.
-
-Example:
-- Before: "CLI and library PRs got no visual evidence because the capture flow assumed a web app with a dev server."
-- After: "Evidence capture now works for any project type -- CLI tools, libraries, desktop apps."
-- Scope: "Shipped with git-commit-push-pr restructuring because ce-demo-reel integrates into the PR description flow."
+This frame becomes the opening. For small+simple PRs, the "after" sentence alone may be the entire description.
 
 #### Sizing the change
 
-The description must be **adaptive** -- its depth should match the complexity of the change. A one-line bugfix does not need a table of performance results. A large architectural change should not be a bullet list.
-
-Assess the PR along two axes before writing, based on the full branch diff:
-
-- **Size**: How many files changed? How large is the diff?
-- **Complexity**: Is this a straightforward change (rename, dependency bump, typo fix) or does it involve design decisions, trade-offs, new patterns, or cross-cutting concerns?
-
-Use this to select the right description depth:
+Assess size (files, diff volume) and complexity (design decisions, trade-offs, cross-cutting concerns) to select description depth:
 
 | Change profile | Description approach |
 |---|---|
-| Small + simple (typo, config, dep bump) | 1-2 sentences, no headers. Total body under ~300 characters. |
-| Small + non-trivial (targeted bugfix, behavioral change) | Short "Problem / Fix" narrative, ~3-5 sentences. Enough for a reviewer to understand *why* without reading the diff. No headers needed unless there are two distinct concerns. |
-| Medium feature or refactor | Open with the narrative frame (before/after/scope), then a section explaining what changed and why. Call out design decisions. |
-| Large or architecturally significant | Full narrative: problem context, approach chosen (and why), key decisions, migration notes or rollback considerations if relevant. |
-| Performance improvement | Include before/after measurements if available. A markdown table is effective here. |
+| Small + simple (typo, config, dep bump) | 1-2 sentences, no headers. Under ~300 characters. |
+| Small + non-trivial (bugfix, behavioral change) | Short narrative, ~3-5 sentences. No headers unless two distinct concerns. |
+| Medium feature or refactor | Narrative frame (before/after/scope), then what changed and why. Call out design decisions. |
+| Large or architecturally significant | Full narrative: problem context, approach (and why), key decisions, migration/rollback if relevant. |
+| Performance improvement | Include before/after measurements if available. Markdown table works well. |
 
-**Brevity matters for small changes.** A 3-line bugfix with a 20-line PR description signals the author didn't calibrate. Match the weight of the description to the weight of the change. When in doubt, shorter is better -- reviewers can read the diff.
+When in doubt, shorter is better. Match description weight to change weight.
 
 #### Writing voice
 
-If the user has documented writing style preferences (in CLAUDE.md, project instructions, or prior feedback), follow those. Otherwise, apply these defaults:
+If the user has documented style preferences, follow those. Otherwise:
 
-- Use active voice throughout. No em dashes or double-hyphen (`--`) substitutes. Use periods, commas, colons, or parentheses instead.
-- Vary sentence length deliberately -- mix short punchy sentences with longer ones. Never write three sentences of similar length in a row.
-- Do not make a claim and then immediately explain it in the next sentence. Trust the reader.
-- Write in plain English. If there's a simpler word, that's preferable. Never use business jargon when a common word will do. Technical jargon is fine when it's the clearest term for a developer audience.
-- No filler phrases: "it's worth noting", "importantly", "essentially", "in order to", "leverage", "utilize."
-- Use digits for numbers ("3 files", "7 subcommands"), not words ("three files", "seven subcommands").
+- Active voice. No em dashes or `--` substitutes; use periods, commas, colons, or parentheses.
+- Vary sentence length. Never three similar-length sentences in a row.
+- Do not make a claim and immediately explain it. Trust the reader.
+- Plain English. Technical jargon fine; business jargon never.
+- No filler: "it's worth noting", "importantly", "essentially", "in order to", "leverage", "utilize."
+- Digits for numbers ("3 files"), not words ("three files").
 
 #### Writing principles
 
-- **Lead with value**: The first sentence should tell the reviewer *what's now possible or fixed*, not what was moved around. "Fixes timeout errors during batch exports" beats "Updated export_handler.py and config.yaml." The subtler failure is leading with the mechanism: "Replace the hardcoded capture block with a tiered skill" is technically purposeful but still doesn't tell the reviewer what changed for users. "Evidence capture now works for CLI tools and libraries, not just web apps" does.
-- **No orphaned opening paragraphs**: If the description uses `##` section headings anywhere, the opening summary must also be under a heading (e.g., `## Summary`). An untitled paragraph followed by titled sections looks like a missing heading. For short descriptions with no sections, a bare paragraph is fine.
-- **Describe the net result, not the journey**: The PR description is about the end state -- what changed and why. Do not include work-product details like bugs found and fixed during development, intermediate failures, debugging steps, iteration history, or refactoring done along the way. Those are part of getting the work done, not part of the result. If a bug fix happened during development, the fix is already in the diff -- mentioning it in the description implies it's a separate concern the reviewer should evaluate, when really it's just part of the final implementation. Exception: include process details only when they are critical for a reviewer to understand a design choice (e.g., "tried approach X first but it caused Y, so went with Z instead").
-- **When commits conflict, trust the final diff**: The commit list is supporting context, not the source of truth for the final PR description. If commit messages describe intermediate steps that were later revised or reverted (for example, "switch to gh pr list" followed by a later change back to `gh pr view`), describe the end state shown by the full branch diff. Do not narrate contradictory commit history as if all of it shipped.
-- **Explain the non-obvious**: If the diff is self-explanatory, don't narrate it. Spend description space on things the diff *doesn't* show: why this approach, what was considered and rejected, what the reviewer should pay attention to.
-- **Use structure when it earns its keep**: Headers, bullet lists, and tables are tools -- use them when they aid comprehension, not as mandatory template sections. An empty "## Breaking Changes" section adds noise.
-- **Markdown tables for data**: When there are before/after comparisons, performance numbers, or option trade-offs, a table communicates density well. Example:
-
-  ```markdown
-  | Metric | Before | After |
-  |--------|--------|-------|
-  | p95 latency | 340ms | 120ms |
-  | Memory (peak) | 2.1GB | 1.4GB |
-  ```
-
-- **No empty sections**: If a section (like "Breaking Changes" or "Migration Guide") doesn't apply, omit it entirely. Do not include it with "N/A" or "None".
-- **Test plan -- only when it adds value**: Include a test plan section when the testing approach is non-obvious: edge cases the reviewer might not think of, verification steps for behavior that's hard to see in the diff, or scenarios that require specific setup. Omit it for straightforward changes where the tests are self-explanatory or where "run the tests" is the only useful guidance. A test plan for "verify the typo is fixed" is noise. When the branch adds new test files, name them with what they cover -- "`tests/capture-evidence.test.ts` -- 8 tests covering arg validation and ffmpeg stitch integration" is more useful than "bun test passes."
+- **Lead with value**: Open with what's now possible or fixed, not what was moved around. The subtler failure is leading with the mechanism ("Replace the hardcoded capture block with a tiered skill") instead of the outcome ("Evidence capture now works for CLI tools and libraries, not just web apps").
+- **No orphaned opening paragraphs**: If the description uses `##` headings anywhere, the opening must also be under a heading (e.g., `## Summary`). For short descriptions with no sections, a bare paragraph is fine.
+- **Describe the net result, not the journey**: The description covers the end state, not how you got there. No iteration history, debugging steps, intermediate failures, or bugs found and fixed during development. This applies equally to description updates: rewrite from the current state, not as a log of what changed since the last version. Exception: process details critical to understand a design choice.
+- **When commits conflict, trust the final diff**: The commit list is supporting context, not the source of truth. If commits describe intermediate steps later revised or reverted, describe the end state from the full branch diff.
+- **Explain the non-obvious**: If the diff is self-explanatory, don't narrate it. Spend space on things the diff doesn't show: why this approach, what was rejected, what the reviewer should watch.
+- **Use structure when it earns its keep**: Headers, bullets, and tables aid comprehension, not mandatory template sections.
+- **Markdown tables for data**: Before/after comparisons, performance numbers, or option trade-offs communicate well as tables.
+- **No empty sections**: If a section doesn't apply, omit it. No "N/A" or "None."
+- **Test plan -- only when non-obvious**: Include when testing requires edge cases the reviewer wouldn't think of, hard-to-verify behavior, or specific setup. Omit when "run the tests" is the only useful guidance. When the branch adds test files, name them with what they cover.
 
 #### Visual communication
 
-Include a visual aid when the PR changes something structurally complex enough that a reviewer would struggle to reconstruct the mental model from prose alone. Visual aids are conditional on content patterns -- what the PR changes -- not on PR size. A small PR that restructures a complex workflow may warrant a diagram; a large mechanical refactor may not.
-
-The bar for including visual aids in PR descriptions is higher than in brainstorms or plans. Reviewers scan PR descriptions to orient before reading the diff -- visuals must earn their space quickly.
+Include a visual aid only when the change is structurally complex enough that a reviewer would struggle to reconstruct the mental model from prose alone.
 
 **When to include:**
 
-| PR changes... | Visual aid | Placement |
-|---|---|---|
-| Architecture touching 3+ interacting components or services | Mermaid component or interaction diagram | Within the approach or changes section |
-| A multi-step workflow, pipeline, or data flow with non-obvious sequencing | Mermaid flow diagram | After the summary or within the changes section |
-| 3+ behavioral modes, states, or variants being introduced or changed | Markdown comparison table | Within the relevant section |
-| Before/after performance data, behavioral differences, or option trade-offs | Markdown table (see the "Markdown tables for data" writing principle above) | Inline with the data being discussed |
-| Data model changes with 3+ related entities or relationship changes | Mermaid ERD or relationship diagram | Within the changes section |
+| PR changes... | Visual aid |
+|---|---|
+| Architecture touching 3+ interacting components | Mermaid component or interaction diagram |
+| Multi-step workflow or data flow with non-obvious sequencing | Mermaid flow diagram |
+| 3+ behavioral modes, states, or variants | Markdown comparison table |
+| Before/after performance or behavioral data | Markdown table |
+| Data model changes with 3+ related entities | Mermaid ERD |
 
 **When to skip:**
-- The change is trivial -- if the sizing table routes to "1-2 sentences", skip visual aids
-- Prose already communicates the change clearly
-- The diagram would just restate the diff in visual form without adding comprehension value
-- The change is mechanical (renames, dependency bumps, config changes, formatting)
-- The PR description is already short enough that a diagram would be heavier than the prose around it
-
-**Format selection:**
-- **Mermaid** (default) for flow diagrams, interaction diagrams, and dependency graphs -- 5-10 nodes typical for a PR description, up to 15 only for genuinely complex changes. Use `TB` (top-to-bottom) direction so diagrams stay narrow in both rendered and source form. Source should be readable as fallback in diff views, email notifications, and Slack previews.
-- **ASCII/box-drawing diagrams** for annotated flows that need rich in-box content -- decision logic branches, file path layouts, step-by-step transformations with annotations. More expressive than mermaid when the diagram's value comes from annotations within steps. Follow 80-column max for code blocks, use vertical stacking.
-- **Markdown tables** for mode/variant comparisons, before/after data, and decision matrices.
-- Keep diagrams proportionate to the change. A PR touching a 5-component interaction gets 5-8 nodes. A larger architectural change may need 10-15 nodes -- that is fine if every node earns its place.
-- Place inline at the point of relevance within the description, not in a separate "Diagrams" section.
-- Prose is authoritative: when a visual aid and surrounding description prose disagree, the prose governs.
-
-After generating a visual aid, verify it accurately represents the change described in the PR -- correct components, no missing interactions, no merged steps. Diagrams derived from a diff (rather than from code analysis) carry higher inaccuracy risk.
+- Sizing routes to "1-2 sentences"
+- Prose already communicates clearly
+- The diagram would just restate the diff visually
+- Mechanical changes (renames, dep bumps, config, formatting)
 
-#### Numbering and references
+**Format:**
+- **Mermaid** (default) for flows, interactions, dependencies. 5-10 nodes typical, up to 15 for genuinely complex changes. Use `TB` direction. Source should be readable as fallback.
+- **ASCII diagrams** for annotated flows needing rich in-box content. 80-column max.
+- **Markdown tables** for comparisons and decision matrices.
+- Place inline at point of relevance, not in a separate section.
+- Prose is authoritative when it conflicts with a visual.
 
-**Never prefix list items with `#`** in PR descriptions. GitHub interprets `#1`, `#2`, etc. as issue/PR references and auto-links them. Instead of:
-
-```markdown
-## Changes
-#1. Updated the parser
-#2. Fixed the validation
-```
+Verify generated diagrams against the change before including.
 
-Write:
+#### Numbering and references
 
-```markdown
-## Changes
-1. Updated the parser
-2. Fixed the validation
-```
+Never prefix list items with `#` in PR descriptions -- GitHub interprets `#1`, `#2` as issue references and auto-links them.
 
-When referencing actual GitHub issues or PRs, use the full format: `org/repo#123` or the full URL. Never use bare `#123` unless you have verified it refers to the correct issue in the current repository.
+When referencing actual GitHub issues or PRs, use `org/repo#123` or the full URL. Never use bare `#123` unless verified.
 
 #### Compound Engineering badge
 
-Append a badge footer to the PR description, separated by a `---` rule. Do not add one if the description already contains a Compound Engineering badge (e.g., added by another skill like ce-work).
+Append a badge footer separated by a `---` rule. Skip if a badge already exists.
 
 **Badge:**
 
@@ -382,8 +324,6 @@ Append a badge footer to the PR description, separated by a `---` rule. Do not a
 ![HARNESS](https://img.shields.io/badge/MODEL_SLUG-COLOR?logo=LOGO&logoColor=white)
 ```
 
-Fill in at PR creation time using the harness lookup (for logo and color) and model slug below.
-
 **Harness lookup:**
 
 | Harness | `LOGO` | `COLOR` |
@@ -392,14 +332,7 @@ Fill in at PR creation time using the harness lookup (for logo and color) and mo
 | Codex | (omit logo param) | `000000` |
 | Gemini CLI | `googlegemini` | `4285F4` |
 
-**Model slug:** Replace spaces with underscores in the model name. Append context window and thinking level in parentheses if known, separated by commas. Examples:
-
-- `Opus_4.6_(1M,_Extended_Thinking)`
-- `GPT_5.4_(High)`
-- `Sonnet_4.6_(200K)`
-- `Opus_4.6` (if context and thinking level are unknown)
-- `Gemini_3.1_Pro`
-- `Gemini_3_Flash`
+**Model slug:** Replace spaces with underscores. Append context window and thinking level in parentheses if known. Examples: `Opus_4.6_(1M,_Extended_Thinking)`, `Sonnet_4.6_(200K)`, `Gemini_3.1_Pro`.
 
 ### Step 7: Create or update the PR
 
@@ -417,19 +350,17 @@ EOF
 )"
 ```
 
-Use the badge from the Compound Engineering badge section above. Replace the harness and model badge with values from the lookup tables.
-
-Keep the PR title under 72 characters. The title follows the same convention as commit messages (Step 2).
+Use the badge from the Compound Engineering badge section. Replace harness and model values from the lookup tables. Keep the PR title under 72 characters, following Step 2 conventions.
 
 #### Existing PR (found in Step 3)
 
-The new commits are already on the PR from the push in Step 5. Report the PR URL, then ask the user whether they want the PR description updated to reflect the new changes. Use the platform's blocking question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). If no question tool is available, present the option and wait for the user's reply before proceeding.
+The new commits are already on the PR from Step 5. Report the PR URL, then ask whether to rewrite the description.
 
 - If **yes**:
-  1. Classify commits per "Classify commits before writing" -- the new commits since the last push are often fix-up work (code review fixes, lint fixes) and should not appear as distinct items
-  2. Size the full PR (not just the new commits) using the sizing table in Step 6
-  3. Write the description as if fresh, following Step 6's writing principles -- describe the PR's net result
-  4. Include the Compound Engineering badge unless one is already present
+  1. Classify commits -- new commits since last push are often fix-up work and should not appear as distinct items
+  2. Size the full PR (not just new commits) using the sizing table
+  3. **Rewrite from scratch** to describe the PR's net result as of now, following Step 6's writing principles. Do not append, amend, or layer onto the old description. The description is not a changelog.
+  4. Include the Compound Engineering badge unless already present
   5. Apply:
 
   ```bash
@@ -439,8 +370,8 @@ The new commits are already on the PR from the push in Step 5. Report the PR URL
   )"
   ```
 
-- If **no** -- done. The push was all that was needed.
+- If **no** -- done.
 
 ### Step 8: Report
 
-Output the PR URL so the user can navigate to it directly.
+Output the PR URL.
PATCH

echo "Gold patch applied."
