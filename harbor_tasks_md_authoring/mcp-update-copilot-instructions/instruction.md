# Update copilot instructions

Source: [microsoft/mcp#733](https://github.com/microsoft/mcp/pull/733)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

To leave a reminder about invoking livetests. Related to #697

[This what a PR with these copilot added instructions renders to](https://github.com/scbedd/check-actions/pull/10) with these copilot-instructions added.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
