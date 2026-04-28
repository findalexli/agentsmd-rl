#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aztec-packages

# Idempotency guard
if grep -qF ".claude/agents/analyze-logs.md" ".claude/agents/analyze-logs.md" && grep -qF "- Attempt to fix any failures (just identify them)" ".claude/agents/identify-ci-failures.md" && grep -qF "**You do:** Use the Task tool with `subagent_type: \"analyze-logs\"` and prompt in" ".claude/skills/ci-logs/SKILL.md" && grep -qF "Run `./bootstrap.sh` in `noir` to ensure that the new submodule commit has been " ".claude/skills/noir-sync-update/SKILL.md" && grep -qF "### 1. Determine Target Files" ".claude/skills/updating-changelog/SKILL.md" && grep -qF "LOG_LEVEL='info; debug:sequencer,p2p' yarn workspace @aztec/end-to-end test:e2e " "yarn-project/.claude/skills/debug-e2e/SKILL.md" && grep -qF "gh pr view <PR> --repo AztecProtocol/aztec-packages --json state,baseRefName,hea" "yarn-project/.claude/skills/fix-pr/SKILL.md" && grep -qF "gh pr view <PR> --repo AztecProtocol/aztec-packages --json state,headRefName,bas" "yarn-project/.claude/skills/rebase-pr/SKILL.md" && grep -qF "argument-hint: <task description>" "yarn-project/.claude/skills/worktree-spawn/SKILL.md" && grep -qF "PRs are squashed to a single commit on merge, so during development just create " "yarn-project/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/agents/analyze-logs.md b/.claude/agents/analyze-logs.md
@@ -2,7 +2,6 @@
 name: analyze-logs
 description: |
   Deep-read test logs and extract relevant information. Runs in separate context to avoid polluting the main conversation. Accepts local file paths (preferred) or hashes. Returns condensed summaries, not raw logs.
-model: sonnet
 ---
 
 # CI Log Analysis Agent
diff --git a/.claude/agents/identify-ci-failures.md b/.claude/agents/identify-ci-failures.md
@@ -2,7 +2,6 @@
 name: identify-ci-failures
 description: |
   Identify CI failures from a PR number, CI URL, or log hash. Returns structured list of failures with local file paths for downloaded logs. Use this subagent to find what failed before deeper analysis.
-model: sonnet
 ---
 
 # CI Failure Identification Agent
@@ -46,6 +45,10 @@ Return a structured report:
 [If found in logs, provide the History URL for finding successful runs]
 ```
 
+Do NOT:
+- Return raw multi-thousand-line log dumps
+- Attempt to fix any failures (just identify them)
+
 ## Workflow
 
 ### Step 1: Get CI Log Hash
diff --git a/.claude/skills/ci-logs/SKILL.md b/.claude/skills/ci-logs/SKILL.md
@@ -1,49 +1,26 @@
 ---
 name: ci-logs
 description: Analyze CI logs from ci.aztec-labs.com. Use this instead of WebFetch for CI URLs.
-user-invocable: true
-arguments: <url-or-hash>
+argument-hint: <url-or-hash>
 ---
 
 # CI Log Analysis
 
-When you need to analyze logs from ci.aztec-labs.com, use the Task tool to spawn the analyze-logs agent.
+When you need to analyze logs from ci.aztec-labs.com, delegate to the `analyze-logs` subagent.
 
 ## Usage
 
 1. **Extract the hash** from the URL (e.g., `http://ci.aztec-labs.com/e93bcfdc738dc2e0` → `e93bcfdc738dc2e0`)
 
-2. **Spawn the analyze-logs agent** using the Task tool:
-
-```
-Task(
-  subagent_type: "analyze-logs",
-  prompt: "Analyze CI log hash: <hash>. Focus: errors",
-  description: "Analyze CI logs"
-)
-```
+2. **Spawn the `analyze-logs` subagent** using the Task tool with the hash and focus area (e.g. "errors", "test \<name>", or a custom question) in the prompt.
 
 ## Examples
 
 **User asks:** "What failed in http://ci.aztec-labs.com/343c52b17688d2cd"
 
-**You do:**
-```
-Task(
-  subagent_type: "analyze-logs",
-  prompt: "Analyze CI log hash: 343c52b17688d2cd. Focus: errors. Download with: yarn ci dlog 343c52b17688d2cd > /tmp/343c52b17688d2cd.log",
-  description: "Analyze CI failure"
-)
-```
-
-**For specific test analysis:**
-```
-Task(
-  subagent_type: "analyze-logs",
-  prompt: "Analyze CI log hash: 343c52b17688d2cd. Focus: test 'my test name'",
-  description: "Analyze test failure"
-)
-```
+**You do:** Use the Task tool with `subagent_type: "analyze-logs"` and prompt including the hash `343c52b17688d2cd`, focus on errors, and instruction to download with `yarn ci dlog`.
+
+**For specific test analysis:** Same approach, but set the focus to the test name.
 
 ## Do NOT
 
diff --git a/.claude/skills/noir-sync-update/SKILL.md b/.claude/skills/noir-sync-update/SKILL.md
@@ -5,33 +5,21 @@ description: Perform necessary follow-on updates as a result of updating the noi
 
 # Noir Sync Update
 
-## Workflow
+## Steps
 
-Copy this checklist and track progress:
-
-```
-Noir Sync Update Progress:
-- [ ] Step 1: Ensure that the new submodule commit has been pulled.
-- [ ] Step 2: Update the `Cargo.lock` file in `avm-transpiler`.
-- [ ] Step 3: Update the `yarn.lock` file in `yarn-project`.
-- [ ] Step 4: Format `noir-projects`.
-```
-
-After each step, commit the results.
+After each step, verify with `git status` and commit the results before proceeding.
 
 ## Critical Verification Rules
 
 **ALWAYS verify file changes with `git status` after any modification step before marking it complete.** Command output showing "updating" does not guarantee the file was written to disk.
 
 **IMPORTANT:** Always run `git status` from the repository root directory, not from subdirectories. Running `git status noir-projects/` from inside `noir-projects/` will fail silently.
 
-### Step 1: Ensure that the new submodule commit has been pulled
-
-Run `./bootstrap.sh` in `noir` to ensure that the new submodule commit has been pulled.
+### 1. Ensure submodule is pulled
 
-This shouldn't update any files such that a commit is necessary.
+Run `./bootstrap.sh` in `noir` to ensure that the new submodule commit has been pulled. This shouldn't produce changes that need committing.
 
-### Step 2: Update `Cargo.lock` in `avm-transpiler`
+### 2. Update `Cargo.lock` in `avm-transpiler`
 
 **Before updating**, determine the expected noir version:
 1. Read `noir/noir-repo/.release-please-manifest.json` to find the expected version (e.g., `1.0.0-beta.18`)
@@ -55,13 +43,13 @@ It's possible that changes in dependencies result in `avm-transpiler` no longer
   - If transient dependency mismatches mean changes to the dependency tree are necessary, then the `Cargo.lock` file in `avm-transpiler` should be modified. **DO NOT MODIFY `noir/noir-repo`**.
   - If updates are necessary due to changes in exports from `noir/noir-repo` packages, then perform the necessary updates to import statements, etc.
 
-### Step 3: Update `yarn.lock` in `yarn-project`
+### 3. Update `yarn.lock` in `yarn-project`
 
 Run `yarn install` in `yarn-project` to update the `yarn.lock` file.
 
 **After running**, verify with `git status yarn-project/yarn.lock` that the file was modified before committing.
 
-### Step 4: Format `noir-projects`
+### 4. Format `noir-projects`
 
 Run `./bootstrap.sh format` in `noir-projects`.
 
diff --git a/.claude/skills/updating-changelog/SKILL.md b/.claude/skills/updating-changelog/SKILL.md
@@ -5,19 +5,9 @@ description: Updates changelog documentation for contract developers and node op
 
 # Updating Changelog
 
-## Workflow
+## Steps
 
-Copy this checklist and track progress:
-
-```
-Changelog Update Progress:
-- [ ] Step 1: Determine target changelog file from .release-please-manifest.json
-- [ ] Step 2: Analyze branch changes (git diff next...HEAD)
-- [ ] Step 3: Generate draft entries for review
-- [ ] Step 4: Edit documentation files after approval
-```
-
-### Step 1: Determine Target Files
+### 1. Determine Target Files
 
 Read `.release-please-manifest.json` to get the version (e.g., `{"." : "4.0.0"}` → edit `v4.md`).
 
@@ -26,7 +16,7 @@ Read `.release-please-manifest.json` to get the version (e.g., `{"." : "4.0.0"}`
 - Aztec contract developers: `docs/docs-developers/docs/resources/migration_notes.md`
 - Node operators and Ethereum contract developers: `docs/docs-network/reference/changelog/v{major}.md`
 
-### Step 2: Analyze Branch Changes
+### 2. Analyze Branch Changes
 
 Run `git diff next...HEAD --stat` for overview, then `git diff next...HEAD` for details.
 
@@ -37,11 +27,11 @@ Run `git diff next...HEAD --stat` for overview, then `git diff next...HEAD` for
 - Deprecations
 - Configuration changes (CLI flags, environment variables)
 
-### Step 3: Generate Draft Entries
+### 3. Generate Draft Entries
 
 Present draft entries for review BEFORE editing files. Match the formatting conventions by reading existing entries in each file.
 
-### Step 4: Edit Documentation
+### 4. Edit Documentation
 
 After approval, add entries to the appropriate files.
 
@@ -66,44 +56,38 @@ Explanation of what changed.
 
 **Impact**: Effect on existing code.
 
-````
-
 **Component tags:** `[Aztec.nr]`, `[Aztec.js]`, `[PXE]`, `[Aztec Node]`, `[AVM]`, `[L1 Contracts]`, `[CLI]`
 
 ## Node Operator Changelog Format
 
 **File:** `docs/docs-network/reference/changelog/v{major}.md`
 
 **Breaking changes:**
-```markdown
+````markdown
 ### Feature Name
 
 **v{previous}:**
 ```bash
 --old-flag <value>                    ($OLD_ENV_VAR)
-````
+```
 
 **v{current}:**
-
 ```bash
 --new-flag <value>                    ($NEW_ENV_VAR)
 ```
 
 **Migration**: How to migrate.
-
 ````
 
 **New features:**
-```markdown
+````markdown
 ### Feature Name
 
 ```bash
 --new-flag <value>                    ($ENV_VAR)
-````
+```
 
 Description of the feature.
-
-```
+````
 
 **Changed defaults:** Use table format with Flag, Environment Variable, Previous, New columns.
-```
diff --git a/yarn-project/.claude/skills/debug-e2e/SKILL.md b/yarn-project/.claude/skills/debug-e2e/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: debug-e2e
 description: Interactive debugging for failed e2e tests. Orchestrates the debugging session but delegates log reading to subagents to keep the main conversation clean. Use for ping-pong debugging sessions where you want to form and test hypotheses together with the user.
+argument-hint: <hash, PR, URL, or test name>
 ---
 
 # E2E Test Debugging
@@ -145,19 +146,17 @@ To understand when a test started failing:
 To run tests locally for verification:
 
 ```bash
-cd end-to-end
-
 # Run specific test
-yarn test:e2e <file>.test.ts -t '<test name>'
+yarn workspace @aztec/end-to-end test:e2e <file>.test.ts -t '<test name>'
 
 # With verbose logging
-LOG_LEVEL=verbose yarn test:e2e <file>.test.ts -t '<test name>'
+LOG_LEVEL=verbose yarn workspace @aztec/end-to-end test:e2e <file>.test.ts -t '<test name>'
 
 # With debug logging (very detailed)
-LOG_LEVEL=debug yarn test:e2e <file>.test.ts -t '<test name>'
+LOG_LEVEL=debug yarn workspace @aztec/end-to-end test:e2e <file>.test.ts -t '<test name>'
 
 # With specific module logging
-LOG_LEVEL='info; debug:sequencer,p2p' yarn test:e2e <file>.test.ts -t '<test name>'
+LOG_LEVEL='info; debug:sequencer,p2p' yarn workspace @aztec/end-to-end test:e2e <file>.test.ts -t '<test name>'
 ```
 
 ## Log Structure
diff --git a/yarn-project/.claude/skills/fix-pr/SKILL.md b/yarn-project/.claude/skills/fix-pr/SKILL.md
@@ -16,6 +16,17 @@ Autonomous workflow to fix CI failures for a PR. Delegates failure identificatio
 
 ## Workflow
 
+### Phase 0: Validate PR
+
+Before doing anything, verify the PR is valid:
+
+```bash
+gh pr view <PR> --repo AztecProtocol/aztec-packages --json state,baseRefName,headRefName
+```
+
+**Abort if:**
+- `state` is not `OPEN` → "PR #\<N> is \<state>, nothing to fix."
+
 ### Phase 1: Identify Failures
 
 Spawn the `identify-ci-failures` subagent:
@@ -37,20 +48,14 @@ This returns:
 ### Phase 2: Checkout and Rebase
 
 ```bash
-# Get PR info
-gh pr view <PR> --repo AztecProtocol/aztec-packages --json headRefName,baseRefName
-
-# Checkout PR
 gh pr checkout <PR>
-
-# Rebase on base branch
 git fetch origin <base-branch>
 git rebase origin/<base-branch>
 ```
 
 If there are conflicts:
 1. Resolve the conflicts
-2. `git add .`
+2. `git add <resolved-files>`
 3. `git rebase --continue`
 
 **Important**: Always REBASE, never merge.
@@ -73,76 +78,51 @@ Run from `yarn-project` directory.
 
 | Failure Type | Fix Action |
 |-------------|------------|
-| **FORMAT** | `yarn format <package-name>` |
+| **FORMAT** | `yarn format` |
 | **LINT** | `yarn lint` |
 | **BUILD** | `yarn build`, fix TypeScript errors, repeat |
 | **UNIT TEST** | `yarn workspace @aztec/<package> test <file>`, fix, repeat |
 | **E2E TEST** | For simple failures, fix. For complex failures, suggest `/debug-e2e` |
 
-#### Format Errors
-```bash
-yarn format
-```
+### Phase 5: Quality Checklist
 
-#### Lint Errors
-```bash
-yarn lint
-```
+Before committing, run from `yarn-project`:
 
-#### Build Errors
 ```bash
 yarn build
-# Fix errors shown
-yarn build  # Repeat until clean
+yarn format
+yarn lint
 ```
 
-#### Unit Test Errors
+Run tests for modified files:
 ```bash
 yarn workspace @aztec/<package> test <file>.test.ts
-# Fix errors
-yarn workspace @aztec/<package> test <file>.test.ts  # Repeat until passing
-```
-
-#### E2E Test Errors
-
-For simple failures (obvious assertion fix):
-```bash
-yarn workspace @aztec/end-to-end test:e2e <file>.test.ts -t '<test name>'
-# Fix and repeat
 ```
 
-For complex failures (flaky, timeout, unclear cause):
-- Inform the user that this needs deeper investigation
-- Suggest using `/debug-e2e` skill instead
-
-### Phase 5: Quality Checklist
-
-Before committing, run from `yarn-project`:
+### Phase 6: Commit and Push
 
-```bash
-yarn build                              # Ensure it compiles
-yarn format                             # Format modified packages
-yarn lint                               # Lint (same as CI)
-```
+If the PR targets `next`, amend to keep it as a single commit:
 
-Run tests for modified files:
 ```bash
-yarn workspace @aztec/<package> test <file>.test.ts
+git add .
+git commit --amend --no-edit
+git push --force-with-lease
 ```
 
-### Phase 6: Amend and Push
+Otherwise, create a normal commit:
 
 ```bash
 git add .
-git commit --amend --no-edit
-git push --force-with-lease
+git commit -m "fix: <description of fix>"
+git push
 ```
 
 ## Key Points
 
+- **Validate first**: Only fix PRs that are open
 - **Delegate identification**: Use `identify-ci-failures` subagent, don't analyze logs directly
 - **Rebase, don't merge**: Always rebase on the base branch
-- **Amend, don't create new commits**: PRs should be single commits
+- **Amend only for PRs targeting `next`**: Other PRs use normal commits
 - **Bootstrap when needed**: Only if changes outside yarn-project
 - **Escalate e2e failures**: Complex e2e issues need `/debug-e2e`
 
diff --git a/yarn-project/.claude/skills/rebase-pr/SKILL.md b/yarn-project/.claude/skills/rebase-pr/SKILL.md
@@ -16,28 +16,26 @@ Simple workflow to rebase a PR on its base branch, resolve conflicts, and push.
 
 ## Workflow
 
-### Step 1: Get PR Info
+### Step 1: Validate PR
 
 ```bash
-gh pr view <PR> --repo AztecProtocol/aztec-packages --json headRefName,baseRefName
+gh pr view <PR> --repo AztecProtocol/aztec-packages --json state,headRefName,baseRefName
 ```
 
-Note the `baseRefName` (usually `next` or `master`).
+**Abort if:**
+- `state` is not `OPEN` → "PR #\<N> is \<state>, nothing to rebase."
 
-### Step 2: Checkout PR
+Note the `baseRefName` (usually `next` or `merge-train/*`).
 
-```bash
-gh pr checkout <PR>
-```
-
-### Step 3: Rebase on Base Branch
+### Step 2: Checkout and Rebase
 
 ```bash
+gh pr checkout <PR>
 git fetch origin <base-branch>
 git rebase origin/<base-branch>
 ```
 
-### Step 4: Resolve Conflicts (if any)
+### Step 3: Resolve Conflicts (if any)
 
 If there are conflicts:
 
@@ -62,7 +60,7 @@ If there are conflicts:
 
 **Important**: Always REBASE, never merge.
 
-### Step 5: Bootstrap (if needed)
+### Step 4: Bootstrap (if needed)
 
 Check if changes exist outside `yarn-project`:
 ```bash
@@ -74,7 +72,7 @@ If yes, run bootstrap from repo root:
 (cd $(git rev-parse --show-toplevel) && BOOTSTRAP_TO=yarn-project ./bootstrap.sh)
 ```
 
-### Step 6: Verify Build
+### Step 5: Verify Build
 
 Run from `yarn-project`:
 
@@ -84,27 +82,39 @@ yarn build
 
 If there are build errors from the rebase, fix them.
 
-### Step 7: Quality Checklist
+### Step 6: Quality Checklist
 
 Format and lint ALL packages:
 
 ```bash
 yarn format
-yarn lint 
+yarn lint
 ```
 
-### Step 8: Amend and Push
+### Step 7: Commit and Push
+
+If there are changes from build fixes or conflict resolution, commit and push.
+
+If the PR targets `next`, amend to keep it as a single commit:
 
 ```bash
 git add .
 git commit --amend --no-edit
 git push --force-with-lease
 ```
 
+Otherwise, create a normal commit:
+
+```bash
+git add .
+git commit -m "fix: resolve rebase conflicts"
+git push --force-with-lease
+```
+
 ## Key Points
 
 - **Rebase, don't merge**: Always use `git rebase`, never `git merge`
-- **Amend, don't create new commits**: PRs should be single commits
+- **Amend only for PRs targeting `next`**: Other PRs use normal commits
 - **Bootstrap when needed**: Only if there are changes outside yarn-project
 - **Verify build**: Always run `yarn build` after rebase
 - **Force push with lease**: Use `--force-with-lease` for safety
diff --git a/yarn-project/.claude/skills/worktree-spawn/SKILL.md b/yarn-project/.claude/skills/worktree-spawn/SKILL.md
@@ -1,6 +1,7 @@
 ---
 name: worktree-spawn
 description: Spawn an independent Claude instance in a git worktree to work on a task in parallel. Use when the user wants to delegate a task to run independently while continuing the current conversation.
+argument-hint: <task description>
 ---
 
 # Worktree Spawn
diff --git a/yarn-project/CLAUDE.md b/yarn-project/CLAUDE.md
@@ -232,16 +232,14 @@ For PRs with multiple commits that should be preserved (e.g., porting multiple P
 
 ### Fixing PRs
 
-When fixing an existing PR (CI failures, review feedback, etc.), always amend the existing commit - never create new commits.
+PRs are squashed to a single commit on merge, so during development just create normal commits. Only amend when explicitly asked or when using the `/fix-pr` skill on a PR targeting `next`.
 
 ```bash
 git add .
-git commit --amend --no-edit
-git push --force-with-lease
+git commit -m "fix: address review feedback"
+git push
 ```
 
-This keeps the PR as a single commit. CI enforces PRs have a single commit.
-
 ### Breaking Changes
 
 1. Use the `/update-changelog` skill for documenting any breaking changes
PATCH

echo "Gold patch applied."
