# docs: Add comprehensive CLAUDE.md for Claude Code integration

Source: [usecannon/cannon#1830](https://github.com/usecannon/cannon/pull/1830)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Adds a comprehensive CLAUDE.md file to provide guidance to Claude Code when working with this repository.

• Development commands and CLI usage reference
• Architecture overview and key concepts  
• Cannon workflow from setup to publishing
• Cannonfile examples and common patterns

This will help future Claude Code instances understand how to build, test, and deploy with Cannon effectively.

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
