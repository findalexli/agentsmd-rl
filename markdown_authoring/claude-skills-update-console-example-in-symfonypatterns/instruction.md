# Update console example in symfony-patterns

Source: [Jeffallan/claude-skills#164](https://github.com/Jeffallan/claude-skills/pull/164)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/php-pro/references/symfony-patterns.md`

## What to add / change

We have a global handler in symfony, we don't need handle manually

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
