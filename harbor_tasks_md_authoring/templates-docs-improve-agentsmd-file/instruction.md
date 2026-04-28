# docs: improve AGENTS.md file

Source: [Domain-Connect/Templates#982](https://github.com/Domain-Connect/Templates/pull/982)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Add note about commit message, and explictly deny template testing
hallucination.   Also improve the dc-template-lint check by adding
logo URL reachability check.

Improves: 51861b611d9abedeffb0e71e951d7c792368f04f

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
