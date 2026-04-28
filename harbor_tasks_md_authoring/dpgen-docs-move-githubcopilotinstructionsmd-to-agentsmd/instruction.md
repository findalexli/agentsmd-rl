# docs: move .github/copilot-instructions.md to AGENTS.md

Source: [deepmodeling/dpgen#1818](https://github.com/deepmodeling/dpgen/pull/1818)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This PR moves the GitHub Copilot instructions file from `.github/copilot-instructions.md` to `AGENTS.md` at the repository root to align with GitHub's new standard for agent instruction files.

## Background

GitHub recently announced support for `AGENTS.md` as a standardized location for custom instructions that can be used by different AI coding agents, not just GitHub Copilot. This change makes the DP-GEN agent instructions more accessible and follows the community standard.

## Changes

- Moved `.github/copilot-instructions.md` → `AGENTS.md`
- All 178 lines of comprehensive DP-GEN instructions are preserved exactly
- The file contains detailed guidance for working with DP-GEN including:
  - Environment setup and installation procedures
  - Core workflows (`dpgen run`, `dpgen autotest`, etc.)
  - Configuration file templates and examples
  - Development requirements and testing procedures
  - Repository structure and common tasks

## Reference

This change implements the feature described in the [GitHub changelog](https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/) where GitHub Copilot Coding Agent now supports `AGENTS.md` custom instructions.

Fixes #1817.

<!-- START COPILOT CODING AGENT TIPS -->
---

💡 You can make Copilot smarter by setting up custom instructions, customizing its development environment and configuring Model Context Protocol (MCP) servers. Learn more [Copilot coding agent tips](https://gh.io/copilo

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
