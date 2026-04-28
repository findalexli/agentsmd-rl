# Add start to cursorrules

Source: [Couchers-org/couchers#7095](https://github.com/Couchers-org/couchers/pull/7095)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursorrules`
- `app/web/.cursorrules`

## What to add / change

I got tired of AI trying to use npm when we use yarn lol.

The idea is we can add to these as we remember best practices.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
