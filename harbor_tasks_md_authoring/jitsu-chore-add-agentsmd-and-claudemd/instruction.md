# chore: add AGENTS.md and CLAUDE.md

Source: [jitsucom/jitsu#1271](https://github.com/jitsucom/jitsu/pull/1271)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Adds AGENTS.md with project structure, tooling, and dev commands overview. CLAUDE.md is a git symlink to AGENTS.md.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
