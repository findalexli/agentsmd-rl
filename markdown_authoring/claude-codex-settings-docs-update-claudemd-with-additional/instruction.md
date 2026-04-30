# docs: update CLAUDE.md with additional guidance

Source: [fcakyon/claude-codex-settings#16](https://github.com/fcakyon/claude-codex-settings/pull/16)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
Update CLAUDE.md with clearer guidance for avoiding certain terminology and accessing Slack resources through MCP tools.

## Changes
- Add "flexible" and "comprehensive" to the word exclusion list for docstrings and commit messages
- Add Slack MCP tools guidance for proper message access patterns
- Simplify docstring header phrase to remove redundancy

## Details
- Word exclusion: Extended the list to help maintain consistent writing quality across docstrings and commit messages
- Slack guidance: Added clear instruction to use `mcp__slack__slack_search_messages` first when accessing Slack URLs or messages
- Docstring header: Changed "Use Google-style docstrings with comprehensive specifications" to "Use Google-style docstrings:" to avoid the word being excluded

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
