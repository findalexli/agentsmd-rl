# docs: add no commit scopes rule to copilot instructions

Source: [camunda/camunda#51712](https://github.com/camunda/camunda/pull/51712)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds the missing `scope-empty` constraint to the Commit Conventions section of `.github/copilot-instructions.md`.

commitlint enforces `scope-empty` in this repo, but the copilot instructions only listed commit types without mentioning that scopes are not allowed — contributors and AI tools reading these instructions would not know.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
