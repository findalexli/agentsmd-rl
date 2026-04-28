# Add AGENTS.md for AI coding agent guidance

Source: [idno/idno#3340](https://github.com/idno/idno/pull/3340)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Comprehensive project documentation for AI agents covering architecture, build/test commands, plugin system, content types, ActivityPub federation, IndieWeb standards, code style, configuration, and security conventions.

https://claude.ai/code/session_01JQWjasJ6H6ofb9WXghW85a

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
