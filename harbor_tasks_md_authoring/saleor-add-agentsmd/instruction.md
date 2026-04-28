# Add agents.md

Source: [saleor/saleor#18193](https://github.com/saleor/saleor/pull/18193)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Adds `AGENTS.md` file which is [a popular standard respected by many agents](https://agents.md/). 

Claude.md now references agents.md because [they don't support it yet](https://github.com/anthropics/claude-code/issues/6235)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
