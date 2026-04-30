# Add AGENTS.md

Source: [sensiolabs/GotenbergBundle#189](https://github.com/sensiolabs/GotenbergBundle/pull/189)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

| Q                       | A        |
|-------------------------|----------|
| Gotenberg API version ? | 8.x      |
| Bug fix ?               | no   |
| New feature ?           | no   |
| BC break ?              | no   |

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
