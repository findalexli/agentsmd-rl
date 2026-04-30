# docs: move copilot-instructions.md to AGENTS.md

Source: [deepmodeling/deepmd-kit#4982](https://github.com/deepmodeling/deepmd-kit/pull/4982)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This PR moves `.github/copilot-instructions.md` to `AGENTS.md` in the repository root to follow the standard convention used by different AI agents.

## Background

According to the [GitHub blog post](https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/), `AGENTS.md` is the commonly used filename for agent instructions that can be recognized by various AI coding agents, not just GitHub Copilot.

## Changes

- Moved `.github/copilot-instructions.md` to `AGENTS.md` in the repository root
- Preserved all existing content exactly (191 lines of detailed instructions)
- Removed the old file location

## Benefits

- Makes agent instructions discoverable by multiple AI coding agents
- Follows the established convention in the AI development community
- Maintains all the valuable build, test, and development guidance for the DeePMD-kit repository

No functional changes were made - this is purely a file relocation to improve discoverability and standardization.

Fixes #4981.

<!-- START COPILOT CODING AGENT TIPS -->
---

💡 You can make Copilot smarter by setting up custom instructions, customizing its development environment and configuring Model Context Protocol (MCP) servers. Learn more [Copilot coding agent tips](https://gh.io/copilot-coding-agent-tips) in the docs.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
