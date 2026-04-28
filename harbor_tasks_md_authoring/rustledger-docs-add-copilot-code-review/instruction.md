# docs: add Copilot code review request instructions

Source: [rustledger/rustledger#661](https://github.com/rustledger/rustledger/pull/661)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Add `gh pr edit --add-reviewer @copilot` instructions to CLAUDE.md review section.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
