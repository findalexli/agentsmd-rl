# docs: streamline PR workflow

Source: [ajhcs/healthcare-agents#15](https://github.com/ajhcs/healthcare-agents/pull/15)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Document the branch -> PR -> merge -> sync path for future edits
- Explicitly avoid local pre-PR merges that create duplicate merge commits and ahead/behind divergence

## Validation
- Documentation-only change

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
