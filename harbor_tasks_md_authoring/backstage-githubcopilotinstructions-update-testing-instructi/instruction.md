# github/copilot-instructions: update testing instructions

Source: [backstage/backstage#31307](https://github.com/backstage/backstage/pull/31307)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Hey, I just made a Pull Request!

Minor update to make the instructions a bit more universal, since all agents don't support running tests in watch mode.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
