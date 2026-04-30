# docs: init CLAUDE.md

Source: [azerothcore/azerothcore-wotlk#24630](https://github.com/azerothcore/azerothcore-wotlk/pull/24630)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

This is the result of the `/init` run for the first time using Claude Opus 4.6, which can be further improved and customised.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
