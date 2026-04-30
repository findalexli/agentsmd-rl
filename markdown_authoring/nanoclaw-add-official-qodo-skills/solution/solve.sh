#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "description: \"Loads org- and repo-level coding rules from Qodo before code tasks" ".claude/skills/get-qodo-rules/SKILL.md" && grep -qF "Rules loaded: **{TOTAL_RULES}** (universal, org level, repo level, and path leve" ".claude/skills/get-qodo-rules/references/output-format.md" && grep -qF "If total rules == 0, inform the user no rules are configured for the repository " ".claude/skills/get-qodo-rules/references/pagination.md" && grep -qF "If the current working directory is inside a `modules/*` subdirectory relative t" ".claude/skills/get-qodo-rules/references/repository-scope.md" && grep -qF "- Implement the fix by **executing the Qodo agent prompt as a direct instruction" ".claude/skills/qodo-pr-resolver/SKILL.md" && grep -qF "This document contains all provider-specific CLI commands and API interactions f" ".claude/skills/qodo-pr-resolver/resources/providers.md" && grep -qF "| `/get-qodo-rules` | Load org- and repo-level coding rules from Qodo before cod" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/get-qodo-rules/SKILL.md b/.claude/skills/get-qodo-rules/SKILL.md
@@ -0,0 +1,122 @@
+---
+name: get-qodo-rules
+description: "Loads org- and repo-level coding rules from Qodo before code tasks begin, ensuring all generation and modification follows team standards. Use before any code generation or modification task when rules are not already loaded. Invoke when user asks to write, edit, refactor, or review code, or when starting implementation planning."
+version: 2.0.0
+allowed-tools: ["Bash"]
+triggers:
+  - "get.?qodo.?rules"
+  - "get.?rules"
+  - "load.?qodo.?rules"
+  - "load.?rules"
+  - "fetch.?qodo.?rules"
+  - "fetch.?rules"
+  - "qodo.?rules"
+  - "coding.?rules"
+  - "code.?rules"
+  - "before.?cod"
+  - "start.?coding"
+  - "write.?code"
+  - "implement"
+  - "create.*code"
+  - "build.*feature"
+  - "add.*feature"
+  - "fix.*bug"
+  - "refactor"
+  - "modify.*code"
+  - "update.*code"
+---
+
+# Get Qodo Rules Skill
+
+## Description
+
+Fetches repository-specific coding rules from the Qodo platform API before code generation or modification tasks. Rules include security requirements, coding standards, quality guidelines, and team conventions that must be applied during code generation.
+**Use** before any code generation or modification task when rules are not already loaded. Invoke when user asks to write, edit, refactor, or review code, or when starting implementation planning.
+**Skip** if "Qodo Rules Loaded" already appears in conversation context
+
+---
+
+## Workflow
+
+### Step 1: Check if Rules Already Loaded
+
+If rules are already loaded (look for "Qodo Rules Loaded" in recent messages), skip to step 6.
+
+### Step 2: Verify working in a git repository
+
+- Check that the current directory is inside a git repository. If not, inform the user that a git repository is required and exit gracefully.
+- Extract the repository scope from the git `origin` remote URL. If no remote is found, exit silently. If the URL cannot be parsed, inform the user and exit gracefully.
+- Detect module-level scope: if inside a `modules/*` subdirectory, use it as the query scope; otherwise use repository-wide scope.
+
+See [repository scope detection](references/repository-scope.md) for details.
+
+### Step 3: Verify Qodo Configuration
+
+Check that the required Qodo configuration is present. The default location is `~/.qodo/config.json`.
+
+- **API key**: Read from `~/.qodo/config.json` (`API_KEY` field). If not found, inform the user that an API key is required and provide setup instructions, then exit gracefully.
+- **Environment name**: Read from `~/.qodo/config.json` (`ENVIRONMENT_NAME` field), with `QODO_ENVIRONMENT_NAME` environment variable taking precedence. If not found, inform the user that an API key is required and provide setup instructions, then exit gracefully.
+
+### Step 4: Fetch Rules with Pagination
+
+- Fetch all pages from the API (50 rules per page) until no more results are returned.
+- On each page, handle HTTP errors and exit gracefully with a user-friendly message.
+- Accumulate all rules across pages into a single list.
+- Stop after 100 pages maximum (safety limit).
+- If no rules are found after all pages, inform the user and exit gracefully.
+
+See [pagination details](references/pagination.md) for the full algorithm and error handling.
+
+### Step 5: Format and Output Rules
+
+- Print the "📋 Qodo Rules Loaded" header with repository scope, scope context, and total rule count.
+- Group rules by severity and print each non-empty group: ERROR, WARNING, RECOMMENDATION.
+- Each rule is formatted as: `- **{name}** ({category}): {description}`
+- End output with `---`.
+
+See [output format details](references/output-format.md) for the exact format.
+
+### Step 6: Apply Rules by Severity
+
+| Severity | Enforcement | When Skipped |
+|---|---|---|
+| **ERROR** | Must comply, non-negotiable. Add comment documenting compliance (e.g., `# Following Qodo rule: No Hardcoded Credentials`) | Explain to user and ask for guidance |
+| **WARNING** | Should comply by default | Briefly explain why in response |
+| **RECOMMENDATION** | Consider when appropriate | No action needed |
+
+### Step 7: Report
+
+After code generation, inform the user about rule application:
+- **ERROR rules applied**: List which rules were followed
+- **WARNING rules skipped**: Explain why
+- **No rules applicable**: Inform: "No Qodo rules were applicable to this code change"
+- **RECOMMENDATION rules**: Mention only if they influenced a design decision
+
+---
+
+## How Scope Levels Work
+
+Determines scope from git remote and working directory (see [Step 2](#step-2-verify-working-in-a-git-repository)):
+
+**Scope Hierarchy**:
+- **Universal** (`/`) - applies everywhere
+- **Org Level** (`/org/`) - applies to organization
+- **Repo Level** (`/org/repo/`) - applies to repository
+- **Path Level** (`/org/repo/path/`) - applies to specific paths
+
+---
+
+## Configuration
+
+See `~/.qodo/config.json` for API key setup. Set `QODO_ENVIRONMENT_NAME` env var or `ENVIRONMENT_NAME` in config to select environment.
+
+---
+
+## Common Mistakes
+
+- **Re-running when rules are loaded** - Check for "Qodo Rules Loaded" in context first
+- **Missing compliance comments on ERROR rules** - ERROR rules require a comment documenting compliance
+- **Forgetting to report when no rules apply** - Always inform the user when no rules were applicable, so they know the rules system is active
+- **Not in git repo** - Inform the user that a git repository is required and exit gracefully; do not attempt code generation
+- **No API key** - Inform the user with setup instructions; set `QODO_API_KEY` or create `~/.qodo/config.json`
+- **No rules found** - Inform the user; set up rules at app.qodo.ai
diff --git a/.claude/skills/get-qodo-rules/references/output-format.md b/.claude/skills/get-qodo-rules/references/output-format.md
@@ -0,0 +1,41 @@
+# Formatting and Outputting Rules
+
+## Output Structure
+
+Print the following header:
+
+```
+# 📋 Qodo Rules Loaded
+
+Scope: `{QUERY_SCOPE}`
+Rules loaded: **{TOTAL_RULES}** (universal, org level, repo level, and path level rules)
+
+These rules must be applied during code generation based on severity:
+```
+
+## Grouping by Severity
+
+Group rules into three sections and print each non-empty section:
+
+**ERROR** (`severity == "error"`):
+```
+## ❌ ERROR Rules (Must Comply) - {count}
+
+- **{name}** ({category}): {description}
+```
+
+**WARNING** (`severity == "warning"`):
+```
+## ⚠️  WARNING Rules (Should Comply) - {count}
+
+- **{name}** ({category}): {description}
+```
+
+**RECOMMENDATION** (`severity == "recommendation"`):
+```
+## 💡 RECOMMENDATION Rules (Consider) - {count}
+
+- **{name}** ({category}): {description}
+```
+
+End output with `---`.
diff --git a/.claude/skills/get-qodo-rules/references/pagination.md b/.claude/skills/get-qodo-rules/references/pagination.md
@@ -0,0 +1,33 @@
+# Fetching Rules with Pagination
+
+The API returns rules in pages of 50. All pages must be fetched to ensure no rules are missed.
+
+## Algorithm
+
+1. Start with `page=1`, `page_size=50`, accumulate results in an empty list
+2. Request: `GET {API_URL}/rules?scopes={ENCODED_SCOPE}&state=active&page={PAGE}&page_size=50`
+   - Header: `Authorization: Bearer {API_KEY}`
+3. On non-200 response, handle the error and exit gracefully:
+   - `401` — invalid/expired API key
+   - `403` — access forbidden
+   - `404` — endpoint not found (check `QODO_ENVIRONMENT_NAME`)
+   - `429` — rate limit exceeded
+   - `5xx` — API temporarily unavailable
+   - connection error — check internet connection
+4. Parse `rules` array from JSON response body
+5. Append page rules to accumulated list
+6. If rules returned on this page < 50 → last page, stop
+7. Otherwise increment page and repeat from step 2
+8. Safety limit: stop after 100 pages (5000 rules max)
+
+## API URL
+
+Construct `{API_URL}` from `ENVIRONMENT_NAME` (read from `~/.qodo/config.json`):
+
+| `ENVIRONMENT_NAME` | `{API_URL}` |
+|---|---|
+| set (e.g. `staging`) | `https://qodo-platform.staging.qodo.ai/rules/v1` |
+
+## After Fetching
+
+If total rules == 0, inform the user no rules are configured for the repository scope and exit gracefully.
diff --git a/.claude/skills/get-qodo-rules/references/repository-scope.md b/.claude/skills/get-qodo-rules/references/repository-scope.md
@@ -0,0 +1,26 @@
+# Repository Scope Detection
+
+## Extracting Repository Scope from Git Remote URL
+
+Parse the `origin` remote URL to derive the scope path. Both URL formats are supported:
+
+- SSH: `git@github.com:org/repo.git` → `/org/repo/`
+- HTTPS: `https://github.com/org/repo.git` → `/org/repo/`
+
+If no remote is found, exit silently. If the URL cannot be parsed, inform the user and exit gracefully.
+
+## Module-Level Scope Detection
+
+If the current working directory is inside a `modules/*` subdirectory relative to the repository root, use it as the query scope:
+
+- `modules/rules/src/service.py` → query scope: `/org/repo/modules/rules/`
+- repository root or any other path → query scope: `/org/repo/`
+
+## Scope Hierarchy
+
+The API returns all rules matching the query scope via prefix matching:
+
+| Query scope | Rules returned |
+|---|---|
+| `/org/repo/modules/rules/` | universal + org + repo + path-level rules |
+| `/org/repo/` | universal + org + repo-level rules |
diff --git a/.claude/skills/qodo-pr-resolver/SKILL.md b/.claude/skills/qodo-pr-resolver/SKILL.md
@@ -0,0 +1,326 @@
+---
+name: qodo-pr-resolver
+description: Review and resolve PR issues with Qodo - get AI-powered code review issues and fix them interactively (GitHub, GitLab, Bitbucket, Azure DevOps)
+version: 0.3.0
+triggers:
+  - qodo.?pr.?resolver
+  - pr.?resolver
+  - resolve.?pr
+  - qodo.?fix
+  - fix.?qodo
+  - qodo.?review
+  - review.?qodo
+  - qodo.?issues?
+  - show.?qodo
+  - get.?qodo
+  - qodo.?resolve
+---
+
+# Qodo PR Resolver
+
+Fetch Qodo review issues for your current branch's PR/MR, fix them interactively or in batch, and reply to each inline comment with the decision. Supports GitHub, GitLab, Bitbucket, and Azure DevOps.
+
+## Prerequisites
+
+### Required Tools:
+- **Git** - For branch operations
+- **Git Provider CLI** - One of: `gh` (GitHub), `glab` (GitLab), `bb` (Bitbucket), or `az` (Azure DevOps)
+
+**Installation and authentication details:** See [providers.md](./resources/providers.md) for provider-specific setup instructions.
+
+### Required Context:
+- Must be in a git repository
+- Repository must be hosted on a supported git provider (GitHub, GitLab, Bitbucket, or Azure DevOps)
+- Current branch must have an open PR/MR
+- PR/MR must have been reviewed by Qodo (pr-agent-pro bot, qodo-merge[bot], etc.)
+
+### Quick Check:
+```bash
+git --version                                    # Check git installed
+git remote get-url origin                        # Identify git provider
+```
+
+See [providers.md](./resources/providers.md) for provider-specific verification commands.
+
+## Understanding Qodo Reviews
+
+Qodo (formerly Codium AI) is an AI-powered code review tool that analyzes PRs/MRs with compliance checks, bug detection, and code quality suggestions.
+
+### Bot Identifiers
+Look for comments from: **`pr-agent-pro`**, **`pr-agent-pro-staging`**, **`qodo-merge[bot]`**, **`qodo-ai[bot]`**
+
+### Review Comment Types
+1. **PR Compliance Guide** 🔍 - Security/ticket/custom compliance with 🟢/🟡/🔴/⚪ indicators
+2. **PR Code Suggestions** ✨ - Categorized improvements with importance ratings
+3. **Code Review by Qodo** - Structured issues with 🐞/📘/📎 sections and agent prompts (most detailed)
+
+## Instructions
+
+When the user asks for a code review, to see Qodo issues, or fix Qodo comments:
+
+### Step 0: Check code push status
+
+Check for uncommitted changes, unpushed commits, and get the current branch.
+
+#### Scenario A: Uncommitted changes exist
+
+- Inform: "⚠️ You have uncommitted changes. These won't be included in the Qodo review."
+- Ask: "Would you like to commit and push them first?"
+- If yes: Wait for user action, then proceed to Step 1
+- If no: Warn "Proceeding with review of pushed code only" and continue to Step 1
+
+#### Scenario B: Unpushed commits exist
+
+(no uncommitted changes)
+
+- Inform: "⚠️ You have N unpushed commits. Qodo hasn't reviewed them yet."
+- Ask: "Would you like to push them now?"
+- If yes: Execute `git push`, inform "Pushed! Qodo will review shortly. Please wait ~5 minutes then run this skill again."
+- Exit skill (don't proceed - Qodo needs time to review)
+- If no: Warn "Proceeding with existing PR review" and continue to Step 1
+
+#### Scenario C: Everything pushed
+
+(both uncommitted changes and unpushed commits are empty)
+
+- Proceed to Step 1
+
+### Step 1: Detect git provider
+
+Detect git provider from the remote URL (`git remote get-url origin`).
+
+See [providers.md](./resources/providers.md) for provider detection patterns.
+
+### Step 2: Find the open PR/MR
+
+Find the open PR/MR for this branch using the provider's CLI.
+
+See [providers.md § Find Open PR/MR](./resources/providers.md#find-open-prmr) for provider-specific commands.
+
+### Step 3: Get Qodo review comments
+
+Get the Qodo review comments using the provider's CLI.
+
+Qodo typically posts both a **summary comment** (PR-level, containing all issues) and **inline review comments** (one per issue, attached to specific lines of code). You must fetch both.
+
+See [providers.md § Fetch Review Comments](./resources/providers.md#fetch-review-comments) for provider-specific commands.
+
+Look for comments where the author is "qodo-merge[bot]", "pr-agent-pro", "pr-agent-pro-staging" or similar Qodo bot name.
+
+#### Step 3a: Check if review is still in progress
+
+- If any comment contains "Come back again in a few minutes" or "An AI review agent is analysing this pull request", the review is still running
+- In this case, inform the user: "⏳ Qodo review is still in progress. Please wait a few minutes and try again."
+- Exit early - don't try to parse incomplete reviews
+
+#### Step 3b: Deduplicate issues
+
+Deduplicate issues across summary and inline comments:
+
+- Qodo posts each issue in two places: once in the **summary comment** (PR-level) and once as an **inline review comment** (attached to the specific code line). These will share the same issue title.
+- Qodo may also post multiple summary comments (Compliance Guide, Code Suggestions, Code Review, etc.) where issues can overlap with slightly different wording.
+- Deduplicate by matching on **issue title** (primary key - the same title means the same issue):
+  - If an issue appears in both the summary comment and as an inline comment, merge them into a single issue
+  - Prefer the **inline comment** for file location (it has the exact line context)
+  - Prefer the **summary comment** for severity, type, and agent prompt (it is more detailed)
+  - **IMPORTANT:** Preserve each issue's **inline review comment ID** — you will need it later (Step 8) to reply directly to that comment with the decision
+- Also deduplicate across multiple summary comments by location (file path + line numbers) as a secondary key
+- If the same issue appears in multiple places, combine the agent prompts
+
+### Step 4: Parse and display the issues
+
+- Extract the review body/comments from Qodo's review
+- Parse out individual issues/suggestions
+- **IMPORTANT: Preserve Qodo's exact issue titles verbatim** — do not rename, paraphrase, or summarize them. Use the title exactly as Qodo wrote it.
+- **IMPORTANT: Preserve Qodo's original ordering** — display issues in the same order Qodo listed them. Qodo already orders by severity.
+- Extract location, issue description, and suggested fix
+- Extract the agent prompt from Qodo's suggestion (the description of what needs to be fixed)
+
+#### Severity mapping
+
+Derive severity from Qodo's action level and position:
+
+1. **Action level determines severity range:**
+   - **"Action required"** issues → Can only be 🔴 CRITICAL or 🟠 HIGH
+   - **"Review recommended"** / **"Remediation recommended"** issues → Can only be 🟡 MEDIUM or ⚪ LOW
+   - **"Other"** / **"Advisory comments"** issues → Always ⚪ LOW (lowest priority)
+
+2. **Qodo's position within each action level determines the specific severity:**
+   - Group issues by action level ("Action required" vs "Review recommended" vs "Other")
+   - Within "Action required" and "Review recommended" groups: earlier positions → higher severity, later positions → lower severity
+   - Split point: roughly first half of each group gets the higher severity, second half gets the lower
+   - All "Other" issues are treated as ⚪ LOW regardless of position
+
+**Example:** 7 "Action required" issues would be split as:
+- Issues 1-3: 🔴 CRITICAL
+- Issues 4-7: 🟠 HIGH
+- Result: No MEDIUM or LOW issues (because there are no "Review recommended" or "Other" issues)
+
+**Example:** 5 "Action required" + 3 "Review recommended" + 2 "Other" issues would be split as:
+- Issues 1-2 or 1-3: 🔴 CRITICAL (first ~half of "Action required")
+- Issues 3-5 or 4-5: 🟠 HIGH (second ~half of "Action required")
+- Issues 6-7: 🟡 MEDIUM (first ~half of "Review recommended")
+- Issue 8: ⚪ LOW (second ~half of "Review recommended")
+- Issues 9-10: ⚪ LOW (all "Other" issues)
+
+**Action guidelines:**
+- 🔴 CRITICAL / 🟠 HIGH ("Action required"): Always "Fix"
+- 🟡 MEDIUM ("Review recommended"): Usually "Fix", can "Defer" if low impact
+- ⚪ LOW ("Review recommended" or "Other"): Can be "Defer" unless quick to fix; "Other" issues are lowest priority
+
+#### Output format
+
+Display as a markdown table in Qodo's exact original ordering (do NOT reorder by severity - Qodo's order IS the severity ranking):
+
+```
+Qodo Issues for PR #123: [PR Title]
+
+| # | Severity | Issue Title | Issue Details | Type | Action |
+|---|----------|-------------|---------------|------|--------|
+| 1 | 🔴 CRITICAL | Insecure authentication check | • **Location:** src/auth/service.py:42<br><br>• **Issue:** Authorization logic is inverted | 🐞 Bug ⛨ Security | Fix |
+| 2 | 🔴 CRITICAL | Missing input validation | • **Location:** src/api/handlers.py:156<br><br>• **Issue:** User input not sanitized before database query | 📘 Rule violation ⛯ Reliability | Fix |
+| 3 | 🟠 HIGH | Database query not awaited | • **Location:** src/db/repository.py:89<br><br>• **Issue:** Async call missing await keyword | 🐞 Bug ✓ Correctness | Fix |
+```
+
+### Step 5: Ask user for fix preference
+
+After displaying the table, ask the user how they want to proceed using AskUserQuestion:
+
+**Options:**
+- 🔍 "Review each issue" - Review and approve/defer each issue individually (recommended for careful review)
+- ⚡ "Auto-fix all" - Automatically apply all fixes marked as "Fix" without individual approval (faster, but less control)
+- ❌ "Cancel" - Exit without making changes
+
+**Based on the user's choice:**
+- If "Review each issue": Proceed to Step 6 (manual review)
+- If "Auto-fix all": Skip to Step 7 (auto-fix mode - apply all "Fix" issues automatically using Qodo's agent prompts)
+- If "Cancel": Exit the skill
+
+### Step 6: Review and fix issues (manual mode)
+
+If "Review each issue" was selected:
+
+- For each issue marked as "Fix" (starting with CRITICAL):
+  - Read the relevant file(s) to understand the current code
+  - Implement the fix by **executing the Qodo agent prompt as a direct instruction**. The agent prompt is the fix specification — follow it literally, do not reinterpret or improvise a different solution. Only deviate if the prompt is clearly outdated relative to the current code (e.g. references lines that no longer exist).
+  - Calculate the proposed fix in memory (DO NOT use Edit or Write tool yet)
+  - **Present the fix and ask for approval in a SINGLE step:**
+    1. Show a brief header with issue title and location
+    2. **Show Qodo's agent prompt in full** so the user can verify the fix matches it
+    3. Display current code snippet
+    4. Display proposed change as markdown diff
+    5. Immediately use AskUserQuestion with these options:
+       - ✅ "Apply fix" - Apply the proposed change
+       - ⏭️ "Defer" - Skip this issue (will prompt for reason)
+       - 🔧 "Modify" - User wants to adjust the fix first
+  - **WAIT for user's choice via AskUserQuestion**
+  - **If "Apply fix" selected:**
+    - Apply change using Edit tool (or Write if creating new file)
+    - Reply to the Qodo inline comment with the decision (see Step 8 for inline reply commands)
+    - Git commit the fix: `git add <modified-files> && git commit -m "fix: <issue title>"`
+    - Confirm: "✅ Fix applied, commented, and committed!"
+    - Mark issue as completed
+  - **If "Defer" selected:**
+    - Ask for deferral reason using AskUserQuestion
+    - Reply to the Qodo inline comment with the deferral (see Step 8 for inline reply commands)
+    - Record reason and move to next issue
+  - **If "Modify" selected:**
+    - Inform user they can make changes manually
+    - Move to next issue
+- Continue until all "Fix" issues are addressed or the user decides to stop
+
+#### Important notes
+
+**Single-step approval with AskUserQuestion:**
+- NO native Edit UI (no persistent permissions possible)
+- Each fix requires explicit approval via custom question
+- Clearer options, no risk of accidental auto-approval
+
+**CRITICAL:** Single validation only - do NOT show the diff separately and then ask. Combine the diff display and the question into ONE message. The user should see: brief context → current code → proposed diff → AskUserQuestion, all at once.
+
+**Example:** Show location, Qodo's guidance, current code, proposed diff, then AskUserQuestion with options (✅ Apply fix / ⏭️ Defer / 🔧 Modify). Wait for user choice, apply via Edit tool if approved.
+
+### Step 7: Auto-fix mode
+
+If "Auto-fix all" was selected:
+
+- For each issue marked as "Fix" (starting with CRITICAL):
+  - Read the relevant file(s) to understand the current code
+  - Implement the fix by **executing the Qodo agent prompt as a direct instruction**. The agent prompt is the fix specification — follow it literally, do not reinterpret or improvise a different solution. Only deviate if the prompt is clearly outdated relative to the current code (e.g. references lines that no longer exist).
+  - Apply the fix using Edit tool
+  - Reply to the Qodo inline comment with the decision (see Step 8 for inline reply commands)
+  - Git commit the fix: `git add <modified-files> && git commit -m "fix: <issue title>"`
+  - Report each fix with the agent prompt that was followed:
+    > ✅ **Fixed: [Issue Title]** at `[Location]`
+    > **Agent prompt:** [the Qodo agent prompt used]
+  - Mark issue as completed
+- After all auto-fixes are applied, display summary:
+  - List of all issues that were fixed
+  - List of any issues that were skipped (with reasons)
+
+### Step 8: Post summary to PR/MR
+
+**REQUIRED:** After all issues have been reviewed (fixed or deferred), ALWAYS post a comment summarizing the actions taken, even if all issues were deferred.
+
+See [providers.md § Post Summary Comment](./resources/providers.md#post-summary-comment) for provider-specific commands and summary format.
+
+**After posting the summary, resolve the Qodo review comment:**
+
+Find the Qodo "Code Review by Qodo" comment and mark it as resolved or react to acknowledge it.
+
+See [providers.md § Resolve Qodo Review Comment](./resources/providers.md#resolve-qodo-review-comment) for provider-specific commands.
+
+If resolve fails (comment not found, API error), continue — the summary comment is the important part.
+
+### Step 9: Push to remote
+
+If any fixes were applied (commits were created in Steps 6/7), ask the user if they want to push:
+- If yes: `git push`
+- If no: Inform them they can push later with `git push`
+
+**Important:** If all issues were deferred, there are no commits to push — skip this step.
+
+### Special cases
+
+#### Unsupported git provider
+
+If the remote URL doesn't match GitHub, GitLab, Bitbucket, or Azure DevOps, inform the user and exit.
+
+See [providers.md § Error Handling](./resources/providers.md#error-handling) for details.
+
+#### No PR/MR exists
+
+- Inform: "No PR/MR found for branch `<branch-name>`"
+- Ask: "Would you like me to create a PR/MR?"
+- If yes: Use appropriate CLI to create PR/MR (see [providers.md § Create PR/MR](./resources/providers.md#create-prmr-special-case)), then inform "PR created! Qodo will review it shortly. Run this skill again in ~5 minutes."
+- If no: Exit skill
+
+**IMPORTANT:** Do NOT proceed without a PR/MR
+
+#### No Qodo review yet
+
+- Check if PR/MR has comments from Qodo bots (pr-agent-pro, qodo-merge[bot], etc.)
+- If no Qodo comments found: Inform "Qodo hasn't reviewed this PR/MR yet. Please wait a few minutes for Qodo to analyze it."
+- Exit skill (do NOT attempt manual review)
+
+**IMPORTANT:** This skill only works with Qodo reviews, not manual reviews
+
+#### Review in progress
+
+If "Come back again in a few minutes" message is found, inform user to wait and try again, then exit.
+
+#### Missing CLI tool
+
+If the detected provider's CLI is not installed, provide installation instructions and exit.
+
+See [providers.md § Error Handling](./resources/providers.md#error-handling) for provider-specific installation commands.
+
+#### Inline reply commands
+
+Used per-issue in Steps 6 and 7 to reply to Qodo's inline comments:
+
+Use the inline comment ID preserved during deduplication (Step 3b) to reply directly to Qodo's comment.
+
+See [providers.md § Reply to Inline Comments](./resources/providers.md#reply-to-inline-comments) for provider-specific commands and reply format.
+
+Keep replies short (one line). If a reply fails, log it and continue.
diff --git a/.claude/skills/qodo-pr-resolver/resources/providers.md b/.claude/skills/qodo-pr-resolver/resources/providers.md
@@ -0,0 +1,329 @@
+# Git Provider Commands Reference
+
+This document contains all provider-specific CLI commands and API interactions for the Qodo PR Resolver skill. Reference this file when implementing provider-specific operations.
+
+## Supported Providers
+
+- GitHub (via `gh` CLI)
+- GitLab (via `glab` CLI)
+- Bitbucket (via `bb` CLI)
+- Azure DevOps (via `az` CLI with DevOps extension)
+
+## Provider Detection
+
+Detect the git provider from the remote URL:
+
+```bash
+git remote get-url origin
+```
+
+Match against:
+- `github.com` → GitHub
+- `gitlab.com` → GitLab
+- `bitbucket.org` → Bitbucket
+- `dev.azure.com` → Azure DevOps
+
+## Prerequisites by Provider
+
+### GitHub
+
+**CLI:** `gh`
+- **Install:** `brew install gh` or [cli.github.com](https://cli.github.com/)
+- **Authenticate:** `gh auth login`
+- **Verify:**
+  ```bash
+  gh --version && gh auth status
+  ```
+
+### GitLab
+
+**CLI:** `glab`
+- **Install:** `brew install glab` or [glab.readthedocs.io](https://glab.readthedocs.io/)
+- **Authenticate:** `glab auth login`
+- **Verify:**
+  ```bash
+  glab --version && glab auth status
+  ```
+
+### Bitbucket
+
+**CLI:** `bb` or API access
+- **Install:** See [bitbucket.org/product/cli](https://bitbucket.org/product/cli)
+- **Verify:**
+  ```bash
+  bb --version
+  ```
+
+### Azure DevOps
+
+**CLI:** `az` with DevOps extension
+- **Install:** `brew install azure-cli` or [docs.microsoft.com/cli/azure](https://docs.microsoft.com/cli/azure)
+- **Install extension:** `az extension add --name azure-devops`
+- **Authenticate:** `az login` then `az devops configure --defaults organization=https://dev.azure.com/yourorg project=yourproject`
+- **Verify:**
+  ```bash
+  az --version && az devops
+  ```
+
+## Find Open PR/MR
+
+Get the PR/MR number for the current branch:
+
+### GitHub
+
+```bash
+gh pr list --head <branch-name> --state open --json number,title
+```
+
+### GitLab
+
+```bash
+glab mr list --source-branch <branch-name> --state opened
+```
+
+### Bitbucket
+
+```bash
+bb pr list --source-branch <branch-name> --state OPEN
+```
+
+### Azure DevOps
+
+```bash
+az repos pr list --source-branch <branch-name> --status active --output json
+```
+
+## Fetch Review Comments
+
+Qodo posts both **summary comments** (PR-level) and **inline review comments** (per-line). Fetch both.
+
+### GitHub
+
+```bash
+# PR-level comments (includes the summary comment with all issues)
+gh pr view <pr-number> --json comments
+
+# Inline review comments (per-line comments on specific code)
+gh api repos/{owner}/{repo}/pulls/<pr-number>/comments
+```
+
+### GitLab
+
+```bash
+# All MR notes including inline comments
+glab mr view <mr-iid> --comments
+```
+
+### Bitbucket
+
+```bash
+# All PR comments including inline comments
+bb pr view <pr-id> --comments
+```
+
+### Azure DevOps
+
+```bash
+# PR-level threads (includes summary comments)
+az repos pr show --id <pr-id> --output json
+
+# All PR threads including inline comments
+az repos pr policy list --id <pr-id> --output json
+az repos pr thread list --id <pr-id> --output json
+```
+
+## Reply to Inline Comments
+
+Use the inline comment ID preserved during deduplication to reply directly to Qodo's comments.
+
+### GitHub
+
+```bash
+gh api repos/{owner}/{repo}/pulls/<pr-number>/comments/<inline-comment-id>/replies \
+  -X POST \
+  -f body='<reply-body>'
+```
+
+**Reply format:**
+- **Fixed:** `✅ **Fixed** — <brief description of what was changed>`
+- **Deferred:** `⏭️ **Deferred** — <reason for deferring>`
+
+### GitLab
+
+```bash
+glab api "/projects/:id/merge_requests/<mr-iid>/discussions/<discussion-id>/notes" \
+  -X POST \
+  -f body='<reply-body>'
+```
+
+### Bitbucket
+
+```bash
+bb api "/2.0/repositories/{workspace}/{repo}/pullrequests/<pr-id>/comments" \
+  -X POST \
+  -f 'content.raw=<reply-body>' \
+  -f 'parent.id=<inline-comment-id>'
+```
+
+### Azure DevOps
+
+```bash
+az repos pr thread comment add \
+  --id <pr-id> \
+  --thread-id <thread-id> \
+  --content '<reply-body>'
+```
+
+## Post Summary Comment
+
+After reviewing all issues, post a summary comment to the PR/MR.
+
+### GitHub
+
+```bash
+gh pr comment <pr-number> --body '<comment-body>'
+```
+
+### GitLab
+
+```bash
+glab mr comment <mr-iid> --message '<comment-body>'
+```
+
+### Bitbucket
+
+```bash
+bb pr comment <pr-id> '<comment-body>'
+```
+
+### Azure DevOps
+
+```bash
+az repos pr thread create \
+  --id <pr-id> \
+  --comment-content '<comment-body>'
+```
+
+**Summary format:**
+
+```markdown
+## Qodo Fix Summary
+
+Reviewed and addressed Qodo review issues:
+
+### ✅ Fixed Issues
+- **Issue Title** (Severity) - Brief description of what was fixed
+
+### ⏭️ Deferred Issues
+- **Issue Title** (Severity) - Reason for deferring
+
+---
+*Generated by Qodo PR Resolver skill*
+```
+
+## Resolve Qodo Review Comment
+
+After posting the summary, resolve the main Qodo review comment.
+
+**Steps:**
+1. Fetch all PR/MR comments
+2. Find the Qodo bot comment containing "Code Review by Qodo"
+3. Resolve or react to the comment
+
+### GitHub
+
+```bash
+# 1. Fetch comments to find the comment ID
+gh pr view <pr-number> --json comments
+
+# 2. React with thumbs up to acknowledge
+gh api "repos/{owner}/{repo}/issues/comments/<comment-id>/reactions" \
+  -X POST \
+  -f content='+1'
+```
+
+### GitLab
+
+```bash
+# 1. Fetch discussions to find the discussion ID
+glab api "/projects/:id/merge_requests/<mr-iid>/discussions"
+
+# 2. Resolve the discussion
+glab api "/projects/:id/merge_requests/<mr-iid>/discussions/<discussion-id>" \
+  -X PUT \
+  -f resolved=true
+```
+
+### Bitbucket
+
+```bash
+# Fetch comments via bb api, find the comment ID, then update to resolved status
+bb api "/2.0/repositories/{workspace}/{repo}/pullrequests/<pr-id>/comments/<comment-id>" \
+  -X PUT \
+  -f 'resolved=true'
+```
+
+### Azure DevOps
+
+```bash
+# Mark the thread as resolved
+az repos pr thread update \
+  --id <pr-id> \
+  --thread-id <thread-id> \
+  --status resolved
+```
+
+## Create PR/MR (Special Case)
+
+If no PR/MR exists for the current branch, offer to create one.
+
+### GitHub
+
+```bash
+gh pr create --title '<title>' --body '<body>'
+```
+
+### GitLab
+
+```bash
+glab mr create --title '<title>' --description '<body>'
+```
+
+### Bitbucket
+
+```bash
+bb pr create --title '<title>' --description '<body>'
+```
+
+### Azure DevOps
+
+```bash
+az repos pr create \
+  --title '<title>' \
+  --description '<body>' \
+  --source-branch <branch-name> \
+  --target-branch main
+```
+
+## Error Handling
+
+### Missing CLI Tool
+
+If the detected provider's CLI is not installed:
+1. Inform the user: "❌ Missing required CLI tool: `<cli-name>`"
+2. Provide installation instructions from the Prerequisites section
+3. Exit the skill
+
+### Unsupported Provider
+
+If the remote URL doesn't match any supported provider:
+1. Inform: "❌ Unsupported git provider detected: `<url>`"
+2. List supported providers: GitHub, GitLab, Bitbucket, Azure DevOps
+3. Exit the skill
+
+### API Failures
+
+If inline reply or summary posting fails:
+- Log the error
+- Continue with remaining operations
+- The workflow should not abort due to comment posting failures
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -29,6 +29,8 @@ Single Node.js process that connects to WhatsApp, routes messages to Claude Agen
 | `/customize` | Adding channels, integrations, changing behavior |
 | `/debug` | Container issues, logs, troubleshooting |
 | `/update` | Pull upstream NanoClaw changes, merge with customizations, run migrations |
+| `/qodo-pr-resolver` | Fetch and fix Qodo PR review issues interactively or in batch |
+| `/get-qodo-rules` | Load org- and repo-level coding rules from Qodo before code tasks |
 
 ## Development
 
PATCH

echo "Gold patch applied."
