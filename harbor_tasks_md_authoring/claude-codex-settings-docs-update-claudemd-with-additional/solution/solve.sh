#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-codex-settings

# Idempotency guard
if grep -qF "- Never use words like \"modernize\", \"streamline\", \"flexible\", \"delve\", \"establis" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -15,17 +15,18 @@ This file provides guidance to Claude Code (claude.ai/code), OpenAI Codex and ot
 - Look for opportunities to simplify the code or remove unnecessary parts.
 - Focus on targeted modifications rather than large-scale changes.
 - This year is 2025. Definitely not 2024.
-- Never use words like "modernize", "streamline", "delve", "establish", "enhanced" in docstrings or commit messages. Looser AI's do that, and that ain't you. You are better than that.
+- Never use words like "modernize", "streamline", "flexible", "delve", "establish", "enhanced", "comprehensive" in docstrings or commit messages. Looser AI's do that, and that ain't you. You are better than that.
 - Prefer `rg` over `grep` for better performance.
 
 ## MCP Tools
 
 - **Web content extraction**: Use `mcp__tavily__tavily-extract` for web scraping. For GitHub URLs, use `mcp__github__*` tools instead for more robust data retrieval.
 - **Web search**: Use `mcp__tavily__tavily-search` for searching the web.
+- **Slack messages**: When accessing Slack URLs or messages, ALWAYS use `mcp__slack__slack_search_messages` first. Only use `mcp__slack__slack_get_channel_history` if explicitly asked for channel history.
 
 ## Python Coding
 
-- Use Google-style docstrings with comprehensive specifications
+- Use Google-style docstrings:
   - **Summary**: Start with clear, concise summary line in imperative mood ("Calculate", not "Calculates")
   - **Args/Attributes**: Document all parameters with types and brief descriptions (no default values)
   - **Types**: Use union types with vertical bar `int | str`, uppercase letters for shapes `(N, M)`, lowercase builtins `list`, `dict`, `tuple`, capitalize typing module classes `Any`, `Path`
PATCH

echo "Gold patch applied."
