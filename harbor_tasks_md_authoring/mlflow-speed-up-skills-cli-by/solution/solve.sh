#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotency guard
if grep -qF "Run `uv run --package skills skills --help` to see available commands." ".claude/skills/README.md" && grep -qF "- Bash(uv run --package skills skills fetch-diff:*)" ".claude/skills/add-review-comment/SKILL.md" && grep -qF "uv run --package skills skills analyze-ci 'https://github.com/mlflow/mlflow/acti" ".claude/skills/analyze-ci/SKILL.md" && grep -qF "uv run --package skills skills fetch-diff https://github.com/mlflow/mlflow/pull/" ".claude/skills/fetch-diff/SKILL.md" && grep -qF "uv run --package skills skills fetch-unresolved-comments https://github.com/mlfl" ".claude/skills/fetch-unresolved-comments/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/README.md b/.claude/skills/README.md
@@ -5,7 +5,7 @@ A Python package that provides CLI commands for Claude Code skills.
 ## Usage
 
 ```bash
-uv run skills <command> [args]
+uv run --package skills skills <command> [args]
 ```
 
-Run `uv run skills --help` to see available commands.
+Run `uv run --package skills skills --help` to see available commands.
diff --git a/.claude/skills/add-review-comment/SKILL.md b/.claude/skills/add-review-comment/SKILL.md
@@ -4,7 +4,7 @@ description: Add a review comment to a GitHub pull request.
 allowed-tools:
   - Bash(gh api:*)
   - Bash(gh pr view:*)
-  - Bash(uv run skills fetch-diff:*)
+  - Bash(uv run --package skills skills fetch-diff:*)
 ---
 
 # Add Review Comment
diff --git a/.claude/skills/analyze-ci/SKILL.md b/.claude/skills/analyze-ci/SKILL.md
@@ -2,7 +2,7 @@
 name: analyze-ci
 description: Analyze failed GitHub Action jobs for a pull request.
 allowed-tools:
-  - Bash(uv run skills analyze-ci:*)
+  - Bash(uv run --package skills skills analyze-ci:*)
 ---
 
 # Analyze CI Failures
@@ -19,16 +19,16 @@ This skill analyzes logs from failed GitHub Action jobs using Claude.
 
 ```bash
 # Analyze all failed jobs in a PR
-uv run skills analyze-ci '<pr_url>'
+uv run --package skills skills analyze-ci '<pr_url>'
 
 # Analyze all failed jobs in a workflow run
-uv run skills analyze-ci '<run_url>'
+uv run --package skills skills analyze-ci '<run_url>'
 
 # Analyze specific job URLs directly
-uv run skills analyze-ci '<job_url>' ['<job_url>' ...]
+uv run --package skills skills analyze-ci '<job_url>' ['<job_url>' ...]
 
 # Show debug info (tokens and costs)
-uv run skills analyze-ci '<pr_url>' --debug
+uv run --package skills skills analyze-ci '<pr_url>' --debug
 ```
 
 Output: A concise failure summary with root cause, error messages, test names, and relevant log snippets.
@@ -37,11 +37,11 @@ Output: A concise failure summary with root cause, error messages, test names, a
 
 ```bash
 # Analyze CI failures for a PR
-uv run skills analyze-ci 'https://github.com/mlflow/mlflow/pull/19601'
+uv run --package skills skills analyze-ci 'https://github.com/mlflow/mlflow/pull/19601'
 
 # Analyze a specific workflow run
-uv run skills analyze-ci 'https://github.com/mlflow/mlflow/actions/runs/22626454465'
+uv run --package skills skills analyze-ci 'https://github.com/mlflow/mlflow/actions/runs/22626454465'
 
 # Analyze specific job URLs directly
-uv run skills analyze-ci 'https://github.com/mlflow/mlflow/actions/runs/12345/job/67890'
+uv run --package skills skills analyze-ci 'https://github.com/mlflow/mlflow/actions/runs/12345/job/67890'
 ```
diff --git a/.claude/skills/fetch-diff/SKILL.md b/.claude/skills/fetch-diff/SKILL.md
@@ -2,7 +2,7 @@
 name: fetch-diff
 description: Fetch PR diff with filtering and line numbers for code review.
 allowed-tools:
-  - Bash(uv run skills fetch-diff:*)
+  - Bash(uv run --package skills skills fetch-diff:*)
 ---
 
 # Fetch PR Diff
@@ -12,23 +12,23 @@ Fetches a pull request diff and adds line numbers for easier review comment plac
 ## Usage
 
 ```bash
-uv run skills fetch-diff <pr_url> [--files <pattern> ...]
+uv run --package skills skills fetch-diff <pr_url> [--files <pattern> ...]
 ```
 
 Examples:
 
 ```bash
 # Fetch the full diff
-uv run skills fetch-diff https://github.com/mlflow/mlflow/pull/123
+uv run --package skills skills fetch-diff https://github.com/mlflow/mlflow/pull/123
 
 # Fetch only Python files
-uv run skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files '*.py'
+uv run --package skills skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files '*.py'
 
 # Fetch only frontend files
-uv run skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files 'mlflow/server/js/*'
+uv run --package skills skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files 'mlflow/server/js/*'
 
 # Multiple patterns
-uv run skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files '*.py' '*.ts'
+uv run --package skills skills fetch-diff https://github.com/mlflow/mlflow/pull/123 --files '*.py' '*.ts'
 ```
 
 Token is auto-detected from `GH_TOKEN` env var or `gh auth token`.
diff --git a/.claude/skills/fetch-unresolved-comments/SKILL.md b/.claude/skills/fetch-unresolved-comments/SKILL.md
@@ -2,7 +2,7 @@
 name: fetch-unresolved-comments
 description: Fetch unresolved PR review comments using GitHub GraphQL API, filtering out resolved feedback.
 allowed-tools:
-  - Bash(uv run skills fetch-unresolved-comments:*)
+  - Bash(uv run --package skills skills fetch-unresolved-comments:*)
 ---
 
 # Fetch Unresolved PR Review Comments
@@ -26,13 +26,13 @@ Uses GitHub's GraphQL API to fetch only unresolved review thread comments from a
 2. **Run the skill**:
 
    ```bash
-   uv run skills fetch-unresolved-comments <pr_url>
+   uv run --package skills skills fetch-unresolved-comments <pr_url>
    ```
 
    Example:
 
    ```bash
-   uv run skills fetch-unresolved-comments https://github.com/mlflow/mlflow/pull/18327
+   uv run --package skills skills fetch-unresolved-comments https://github.com/mlflow/mlflow/pull/18327
    ```
 
    The script automatically reads the GitHub token from:
PATCH

echo "Gold patch applied."
