# Add AGENTS.md with comprehensive development guidance

Source: [modelcontextprotocol/ruby-sdk#134](https://github.com/modelcontextprotocol/ruby-sdk/pull/134)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/release-changelogs.mdc`
- `AGENTS.md`

## What to add / change

## Summary

This PR introduces `AGENTS.md`, following the new [agents.md standard](https://agents.md/) for providing AI coding assistant guidance. This replaces the previous Claude-specific documentation with a universal format supported by 20+ AI coding tools.

## Changes Made

- **Added comprehensive `AGENTS.md`** with structured guidance for AI coding assistants including:
  - Project overview and environment setup
  - Build and test commands
  - Code style guidelines and commit conventions
  - Release process documentation
  - Architecture overview with core components
  - Integration patterns and best practices

- **Adopted agents.md standard format** for better compatibility with AI coding tools like:
  - GitHub Copilot
  - Cursor
  - OpenAI Codex
  - VS Code AI extensions
  - And 15+ other tools

- **Consolidated tool-specific rules** by migrating Cursor-specific release changelog guidelines into the universal `AGENTS.md` format and removing `.cursor/rules/release-changelogs.mdc`

## Benefits

1. **Universal compatibility**: Works with any AI coding assistant that supports the agents.md standard
2. **Comprehensive guidance**: Covers development workflow, architecture, testing, and release processes
3. **Improved developer experience**: AI assistants can better understand project structure and conventions
4. **Future-proof**: Follows emerging industry standard for AI coding assistant configuration

## Technical Details

The `AGENTS.md` in

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
