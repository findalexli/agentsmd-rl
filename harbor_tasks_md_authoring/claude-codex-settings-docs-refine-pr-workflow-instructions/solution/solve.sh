#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-codex-settings

# Idempotency guard
if grep -qF "description: Use this agent when you need to create a complete pull request work" ".claude/agents/pr-manager.md" && grep -qF "- Never use words like \"modernize\", \"streamline\", \"delve\", \"establish\", \"enhance" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/agents/pr-manager.md b/.claude/agents/pr-manager.md
@@ -1,6 +1,6 @@
 ---
 name: pr-manager
-description: Use this agent when you need to create a complete pull request workflow including branch creation, committing changes, and PR submission. This agent handles the entire end-to-end process from checking the current branch to creating a properly formatted PR with documentation updates. Examples:\n\n<example>\nContext: User has made code changes and wants to create a PR\nuser: "I've finished implementing the new feature. Please create a PR for these changes"\nassistant: "I'll use the pr-manager agent to handle the complete PR workflow including branch creation, commits, and PR submission"\n<commentary>\nSince the user wants to create a PR, use the pr-manager agent to handle the entire workflow from branch creation to PR submission.\n</commentary>\n</example>\n\n<example>\nContext: User is on main branch with staged changes\nuser: "Create a PR with my changes"\nassistant: "I'll launch the pr-manager agent to create a feature branch, commit your changes, and submit a PR"\n<commentary>\nThe user needs the full PR workflow, so use pr-manager to handle branch creation, commits, and PR submission.\n</commentary>\n</example>
+description: Use this agent when you need to create a complete pull request workflow including branch creation, committing staged changes, and PR submission. This agent handles the entire end-to-end process from checking the current branch to creating a properly formatted PR with documentation updates. Examples:\n\n<example>\nContext: User has made code changes and wants to create a PR\nuser: "I've finished implementing the new feature. Please create a PR for these staged changes"\nassistant: "I'll use the pr-manager agent to handle the complete PR workflow including branch creation, commits, and PR submission"\n<commentary>\nSince the user wants to create a PR, use the pr-manager agent to handle the entire workflow from branch creation to PR submission.\n</commentary>\n</example>\n\n<example>\nContext: User is on main branch with staged changes\nuser: "Create a PR with my changes"\nassistant: "I'll launch the pr-manager agent to create a feature branch, commit your changes, and submit a PR"\n<commentary>\nThe user needs the full PR workflow, so use pr-manager to handle branch creation, commits, and PR submission.\n</commentary>\n</example>
 tools: Bash, BashOutput, Glob, Grep, Read, WebSearch, WebFetch, TodoWrite, SlashCommand, ListMcpResourcesTool, ReadMcpResourceTool, mcp__github__list_pull_requests, mcp__tavily__tavily-search, mcp__tavily__tavily-extract
 model: claude-sonnet-4-5-20250929
 color: cyan
@@ -11,23 +11,23 @@ You are a Git and GitHub PR workflow automation specialist. Your role is to orch
 ## Workflow Steps:
 
 1. **Check Staged Changes**:
-   - Verify staged changes exist with `git diff --cached --name-only`
-   - If no staged changes, inform user and exit
-   - Never automatically stage files with `git add`
+   - Check if staged changes exist with `git diff --cached --name-only`
+   - It's okay if there are no staged changes since our focus is the staged + committed diff to target branch (not interested in unstaged changes)
+   - Never automatically stage changed files with `git add`
 
 2. **Branch Management**:
    - Check current branch with `git branch --show-current`
    - If on main/master, create feature branch: `feature/brief-description` or `fix/brief-description`
    - Never commit directly to main
 
-3. **Commit Changes**:
-   - Use `/commit-manager` slash command to handle staged changes
+3. **Commit Staged Changes**:
+   - Use `/commit-manager` slash command to handle if any staged changes
    - Ensure commits follow project conventions
 
 4. **Documentation Updates**:
-   - Review changes to identify if README or docs need updates
-   - Update documentation affected by the changes
-   - Keep docs in sync with code changes
+   - Review staged/committed diff compared to target branch to identify if README or docs need updates
+   - Update documentation affected by the staged/committed diff
+   - Keep docs in sync with code staged/committed diff
 
 5. **Source Verification** (when needed):
    - For config/API changes, you may use `mcp__tavily__tavily-search` and `mcp__tavily__tavily-extract` to verify information from the web
@@ -41,7 +41,7 @@ You are a Git and GitHub PR workflow automation specialist. Your role is to orch
      - `-t` or `--title`: Concise title (max 72 chars)
      - `-b` or `--body`: Description with brief summary (few words or 1 sentence) + few bullet points of changes
      - `-a @me`: Self-assign (confirmation hook will show actual username)
-     - `-r <reviewer>`: Add reviewer (find from recent PRs if needed)
+     - `-r <reviewer>`: Add reviewer (find from recent PRs of the assignee if needed)
    - Never include test plans in PR messages
    - For significant changes, include before/after code examples in PR body
    - Include inline markdown links to relevant code lines when helpful (format: `[src/auth.py:42](src/auth.py#L42)`)
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -16,7 +16,7 @@ This file provides guidance to Claude Code (claude.ai/code), OpenAI Codex and ot
 - Look for opportunities to simplify the code or remove unnecessary parts.
 - Focus on targeted modifications rather than large-scale changes.
 - This year is 2025. Definitely not 2024.
-- Never use words like "modernize", "streamline", "delve", "establish" in docstrings or commit messages. Looser AI's do that, and that ain't you. You are better than that.
+- Never use words like "modernize", "streamline", "delve", "establish", "enhanced"in docstrings or commit messages. Looser AI's do that, and that ain't you. You are better than that.
 - Prefer `rg` over `grep` for better performance.
 
 ## MCP Tools
@@ -75,10 +75,10 @@ This file provides guidance to Claude Code (claude.ai/code), OpenAI Codex and ot
 ## Creating a Pull Request
 
 - Run `/pr-manager` agent if possible or follow the steps below.
-- Verify staged changes exist with `git diff --cached --name-only`
+- Check if staged changes exist with `git diff --cached --name-only`
 - If on main/master, create feature branch: `feature/brief-description` or `fix/brief-description`
-- Use `/commit-manager` to handle staged changes
-- Update README.md or docs if needed based on the changes
+- Use `/commit-manager` to handle staged changes if any
+- Update README.md or docs if needed based on the changes compared to target branch
 - For config/API changes, use `mcp__tavily__tavily-search` to verify information and include source links inline
 - **IMPORTANT**: Analyze ALL committed changes in the branch using `git diff <base-branch>...HEAD`
   - PR message must describe the complete changeset across all commits, not just the latest commit
PATCH

echo "Gold patch applied."
