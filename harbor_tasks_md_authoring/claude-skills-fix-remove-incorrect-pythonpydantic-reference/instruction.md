# Fix: remove incorrect Python/Pydantic reference in php-pro skill

Source: [Jeffallan/claude-skills#154](https://github.com/Jeffallan/claude-skills/pull/154)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/php-pro/SKILL.md`

## What to add / change

Remove copy-paste error from php-pro SKILL.md.

The MUST NOT DO section contained "Use deprecated features or Pydantic V1 patterns",
which is a Python/FastAPI constraint with no relevance in a PHP context.

Fixes the accuracy of the skill guidelines.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
