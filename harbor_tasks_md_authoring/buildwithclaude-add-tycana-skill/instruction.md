# Add Tycana skill

Source: [davepoon/buildwithclaude#77](https://github.com/davepoon/buildwithclaude/pull/77)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/tycana/SKILL.md`

## What to add / change

## Summary

Adds a Tycana skill to the all-skills collection. Tycana is an AI productivity backend that gives Claude persistent memory about your work via MCP.

**Category:** project-management

## What's included

A `SKILL.md` with:
- Full tool reference (14 MCP tools)
- Example prompts
- Prerequisites and setup
- Key features overview

## Links

- Plugin repo: https://github.com/tycana/tycana-claude-plugin
- Homepage: https://www.tycana.com
- MCP endpoint: https://app.tycana.com/mcp

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
