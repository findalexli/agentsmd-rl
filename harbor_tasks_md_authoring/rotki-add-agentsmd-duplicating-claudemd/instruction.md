# Add AGENTS.md duplicating CLAUDE.md

Source: [rotki/rotki#10547](https://github.com/rotki/rotki/pull/10547)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

This is almost a duplicate of CLAUDE.md since Codex and other tools use AGENTS.md.

Hopefully clause code will also adapt this and we can go back to using a single file: https://github.com/anthropics/claude-code/issues/6235

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
