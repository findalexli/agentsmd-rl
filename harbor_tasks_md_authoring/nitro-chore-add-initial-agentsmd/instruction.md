# chore: add initial `AGENTS.md`

Source: [nitrojs/nitro#3896](https://github.com/nitrojs/nitro/pull/3896)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Actually I'm seeing such thing in many oss projects recently on ai agent guide. I thought maybe such thing we can also implement.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
