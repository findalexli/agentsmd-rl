#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ace

# Idempotency guard
if grep -qF ".cursor/rules/ace-context.mdc" ".cursor/rules/ace-context.mdc" && grep -qF ".cursor/rules/pr-rereview.mdc" ".cursor/rules/pr-rereview.mdc" && grep -qF ".cursor/rules/pr-review.mdc" ".cursor/rules/pr-review.mdc" && grep -qF "To use the PR review rules, configure the GitHub MCP server in Cursor's \"Tools &" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/ace-context.mdc b/.cursor/rules/ace-context.mdc
@@ -1,31 +0,0 @@
----
-description: Context about the ai2cm/ace repository
-globs: ["**/*.py"]
-alwaysApply: true
----
-
-## Repository Context: ai2cm/ace
-
-This is a Python machine learning project for atmospheric modeling (ACE - AI2 Climate Emulator).
-
-### Key Conventions
-
-- Code is in the `fme/` directory (ace, core, coupled, diffusion, downscaling modules)
-- Tests follow pytest conventions
-- Configuration uses YAML files in `configs/`
-- The project uses PyTorch for ML components
-
-### Common Commands
-
-- Run all tests: `make test` or `pytest .`
-- Run fast tests only: `make test_fast` or `pytest --fast .`
-- Run very fast tests: `make test_very_fast` or `pytest --very-fast .`
-- Run tests with coverage: `make test_cov`
-- Create development environment: `make create_environment`
-- Build Docker image: `make build_docker_image`
-
-When available, use the `fme` conda development environment to run tests.
-
-### GitHub MCP Server Setup
-
-To use the PR review rules, configure the GitHub MCP server in Cursor's "Tools & MCP" settings. You will need a read-only personal access token with the following permissions: Pull requests, Issues, Contents, Metadata.
diff --git a/.cursor/rules/pr-rereview.mdc b/.cursor/rules/pr-rereview.mdc
@@ -1,117 +0,0 @@
----
-description: PR Re-review Assistant for ai2cm/ace repository
-globs: []
-alwaysApply: false
----
-
-When asked to re-review a pull request (e.g., "Re-review PR #N" or "Check if my comments were addressed on PR #N"):
-
-## Context Detection
-
-First, determine what context is available:
-
-1. **Previous Review Context Available**: If the current conversation contains a previous PR review or re-review from the Assistant, note those findings to compare against new changes. Ignore any reviews of unrelated PRs.
-
-2. **No Previous Context**: If no previous review context exists, you'll need to fetch all review information from GitHub.
-
-## Instructions
-
-### Step 1: Determine Starting Point
-
-- **If a commit SHA is provided** (e.g., "from commit <SHA>"): Use that as the starting point for reviewing new changes.
-- **If no commit SHA is provided**: Ask the user for the commit SHA where the previous review ended, OR offer to review all changes since the last review comment timestamp.
-
-### Step 2: Fetch PR Data Using GitHub MCP Tools
-
-Use the GitHub MCP server to gather:
-
-1. **PR metadata**: `pull_request_read` with method `get` for current PR state
-2. **New commits**: `list_commits` filtered to commits after the starting point
-3. **New changes**: `get_commit` for each new commit to see the diffs
-4. **Review comments**: `pull_request_read` with method `get_review_comments` to get all review threads
-5. **PR comments**: `pull_request_read` with method `get_comments` for general discussion
-6. **Current diff**: `pull_request_read` with method `get_diff` if needed for full context
-
-### Step 3: Analyze Review Comments
-
-For each review comment thread:
-
-1. **Identify the reviewer's concern**: What was the issue raised?
-2. **Check if resolved**: Look for:
-   - Code changes that address the concern
-   - Author's reply explaining why no change is needed
-   - Thread marked as resolved
-3. **Categorize status**: Addressed, Partially Addressed, Unaddressed, or Dismissed
-
-### Step 4: Compare Against Previous Assistant Review (if available)
-
-If you have context from a previous review in this conversation:
-
-1. Compare your previous findings against new changes
-2. Check if issues you raised were addressed
-3. Note any issues from your review that were NOT addressed in the PR review comments
-4. **Ask the user** if they want to see unaddressed Assistant findings that weren't part of the formal PR review
-
-## Output Format
-
-### Re-review Summary
-
-- PR number and title
-- Commits reviewed: `<starting_sha>...<current_head_sha>`
-- Number of new commits since last review
-
-### New Changes Overview
-
-- Files modified in new commits
-- Brief summary of what changed
-
-### Review Comments Status
-
-#### Addressed Comments
-
-| Comment | File/Line | How Addressed |
-|---------|-----------|---------------|
-| ... | ... | Code change / Author explanation |
-
-#### Unaddressed Comments
-
-| Comment | File/Line | Status | Notes |
-|---------|-----------|--------|-------|
-| ... | ... | Needs attention / Waiting for response | ... |
-
-### New Issues in Recent Changes (if any)
-
-- Any new concerns introduced by the latest commits
-- Follow the same severity categories as pr-review.mdc:
-  - **Critical Issues** (Must Fix)
-  - **Suggestions** (Should Consider)
-  - **Minor/Nitpicks** (Optional)
-
-### Previous Assistant Review Findings (if applicable)
-
-If previous review context exists and some findings were not part of the PR review:
-
-> **Note**: The following issues from the previous Assistant review were not addressed in the PR review comments. Would you like me to include these in the summary?
-> - [List unaddressed Assistant findings]
-
-### Outstanding Items Summary
-
-Clear list of what still needs attention before the PR can be merged:
-
-1. Unaddressed review comments (with links if possible)
-2. New issues found in recent commits
-3. Any blocking items
-
-### Recommendation
-
-- **Ready to merge**: All comments addressed, no blocking issues
-- **Needs minor changes**: Non-blocking items remain
-- **Needs revision**: Blocking issues still unresolved
-
-## Tips
-
-- When fetching review comments, pay attention to the `isResolved` and `isOutdated` fields
-- Author replies that explain design decisions count as "addressed" even without code changes
-- Be concise in the re-review - focus on delta from previous state
-- If the PR has been significantly refactored, consider suggesting a fresh full review instead
-- For large PRs with many commits, consider batching API calls or limiting the number of commits fetched to avoid rate limits
diff --git a/.cursor/rules/pr-review.mdc b/.cursor/rules/pr-review.mdc
@@ -1,69 +0,0 @@
----
-description: PR Review Assistant for ai2cm/ace repository
-globs: []
-alwaysApply: false
----
-
-When asked to review a pull request (e.g., "Review PR #N in the ace repo"):
-
-## Instructions
-
-1. **Fetch PR Data** using GitHub MCP tools:
-   - Get PR description and metadata
-   - Get the full diff/changes
-   - Get all comments and review conversations
-
-2. **Analyze and Output** a structured review with these sections:
-
-### PR Summary
-
-- PR title and number
-- Author
-- Target branch
-- Brief description of what the PR aims to accomplish
-
-### Changes Overview
-
-- List of files modified/added/deleted
-- High-level summary of the changes
-
-### Code Review Findings
-
-#### Critical Issues (Must Fix)
-
-- Security vulnerabilities
-- Bugs or logic errors
-- Breaking changes
-
-#### Suggestions (Should Consider)
-
-- Performance improvements
-- Better error handling
-- Code clarity improvements
-
-#### Minor/Nitpicks (Optional)
-
-- Style inconsistencies
-- Naming suggestions
-- Documentation improvements
-
-### Test Coverage Assessment
-
-- Are there sufficient tests?
-- Are edge cases covered?
-
-### Existing Discussion Summary
-
-- Summarize key points from existing PR comments
-- Note any unresolved concerns
-
-### Recommended Actions
-
-- Clear list of what should be addressed before merge
-
-## Output Format
-
-- Use markdown formatting for readability
-- Reference specific files and line numbers when applicable
-- Be constructive and specific in feedback
-- Distinguish between blocking issues vs suggestions
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,86 @@
+# AGENTS.md
+
+This file is the single source of agent guidance for the `ai2cm/ace` repository.
+
+## Repository Context
+
+This is a Python machine learning project for atmospheric modeling (ACE - AI2 Climate Emulator).
+
+### Key Conventions
+
+- Code is in the `fme/` directory (ace, core, coupled, diffusion, downscaling modules)
+- Tests follow pytest conventions
+- Configuration uses YAML files in `configs/`
+- The project uses PyTorch for ML components
+- The default conda environment for the repo is named `fme`
+
+### Common Commands
+
+- Run all tests: `make test`
+- Run fast tests only: `make test_fast`
+- Run very fast tests: `make test_very_fast`
+- Run tests with coverage: `make test_cov`
+- Create development environment: `make create_environment`
+- Build Docker image: `make build_docker_image`
+
+When running tests in a conda environment, use `python -m pytest` (not `pytest`) to ensure the correct interpreter is used.
+
+### GitHub MCP Server Setup
+
+To use the PR review rules, configure the GitHub MCP server in Cursor's "Tools & MCP" settings. You will need a read-only personal access token with the following permissions: Pull requests, Issues, Contents, Metadata.
+
+## Pull Request Review Assistant
+
+Use this same workflow for both initial review and re-review.
+
+### 1) Gather context with GitHub MCP
+
+- `pull_request_read`:
+  - `get` for metadata/state
+  - `get_diff` for full diff (or current context)
+  - `get_review_comments` for review threads
+  - `get_comments` for general PR discussion
+- `list_commits` and `get_commit` when commit-by-commit analysis is needed
+
+### 2) Scope the review
+
+- **Initial review**: review the full PR diff and all current discussion.
+- **Re-review (delta review)**:
+  - If user provides a starting SHA, review changes from that point.
+  - If not, ask for starting SHA or default to changes since last review comment timestamp.
+  - Focus on what changed, whether prior comments were addressed, and whether new issues were introduced.
+
+### 3) Evaluate findings
+
+Use these severity buckets:
+
+- **Critical Issues (Must Fix)**: security vulnerabilities, logic bugs, breaking changes
+- **Suggestions (Should Consider)**: performance, error handling, clarity/design improvements
+- **Minor/Nitpicks (Optional)**: style, naming, docs polish
+
+For re-reviews, classify prior comments as **Addressed**, **Partially Addressed**, **Unaddressed**, or **Dismissed**. Treat clear author rationale as addressed when appropriate.
+
+### 4) Output format
+
+Write concise markdown with:
+
+1. **PR Summary**: title/number, author, target branch, goal
+2. **Changes Overview**: files changed + high-level summary
+3. **Code Review Findings**: grouped by severity with file/line references
+4. **Discussion Status**: key unresolved comment threads
+5. **Testing Assessment**: gaps and edge cases
+6. **Recommendation**: Ready to merge / Needs minor changes / Needs revision
+
+For re-reviews, include:
+
+- Commits reviewed (`<start_sha>...<head_sha>`)
+- Status of previously raised comments
+- Outstanding items before merge
+
+### 5) Practical guidance
+
+- Be specific, constructive, and explicit about blocking vs non-blocking items.
+- Prefer delta-focused summaries for re-reviews.
+- If the PR was heavily refactored, recommend a fresh full review.
+- For large PRs, batch API calls to avoid rate limits.
+- Remember that GitHub MCP access is read-only.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+@AGENTS.md
PATCH

echo "Gold patch applied."
