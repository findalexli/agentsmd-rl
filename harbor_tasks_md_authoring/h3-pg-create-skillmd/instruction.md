# Create SKILL.md

Source: [postgis/h3-pg#183](https://github.com/postgis/h3-pg/pull/183)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `docs/SKILL.md`

## What to add / change

Here is first iteration of things LLMs in my experience get wrong.

Closes #182

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
