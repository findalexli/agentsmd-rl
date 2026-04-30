# Added AGENTS.md and CLAUDE.md

Source: [TryGhost/Ghost#25107](https://github.com/TryGhost/Ghost/pull/25107)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

no refs

Adds initial draft of `AGENTS.md` file, and adds `CLAUDE.md` as a symlink to keep them in sync. Using symlinks this way should keep the instructions in sync across different agents (claude, codex, gemini, etc).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
