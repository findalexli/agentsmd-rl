# docs: Adapt a11y skill to utilize Lighthouse

Source: [ChromeDevTools/chrome-devtools-mcp#1054](https://github.com/ChromeDevTools/chrome-devtools-mcp/pull/1054)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/a11y-debugging/SKILL.md`

## What to add / change

- **feat: Add Lighthouse audit as the initial step in the accessibility debugging workflow and reorder subsequent sections.**
- **feat: Add critical instructions for parsing Lighthouse audit reports to efficiently extract failing elements.**

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
