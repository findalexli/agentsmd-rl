# Update doc paths in SKILL.md search examples

Source: [prism-php/prism#871](https://github.com/prism-php/prism/pull/871)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `resources/boost/skills/developing-with-prism/SKILL.md`

## What to add / change

Changed documentation references in search examples from `docs/` to `vendor/prism-php/prism/docs/` for correct path resolution.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
