#  Add more instructions to `CLAUDE.md` file

Source: [symfony/ai#433](https://github.com/symfony/ai/pull/433)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

| Q             | A
| ------------- | ---
| Bug fix?      | no
| New feature?  | no
| Docs?         | no
| Issues        | --
| License       | MIT

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
