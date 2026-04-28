# chore: remove CLAUDE.md and AGENTS.md

Source: [always-further/nono#707](https://github.com/always-further/nono/pull/707)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

These two often fall out of sync from not being updated, and research is showing they are not as effective as believed.

Instead we should have the code be the source of truth.

source: arxiv.org/abs/2602.11988

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
