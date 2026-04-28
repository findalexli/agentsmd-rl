# Add comprehensive CLAUDE.md with architecture and commands

Source: [Foundry376/Mailspring#2512](https://github.com/Foundry376/Mailspring/pull/2512)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Document build/test/lint commands, codebase architecture including
Flux pattern (models, stores, tasks, actions), plugin structure,
global exports, and development workflow notes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
