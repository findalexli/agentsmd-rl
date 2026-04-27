# AGENTS.md for non-claude agents

Source: [lemonade-sdk/lemonade#1396](https://github.com/lemonade-sdk/lemonade/pull/1396)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Resolves #1395 

Simply points agents to explore CLAUDE.md for comprehensive information about the project. We avoid duplication this way.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
