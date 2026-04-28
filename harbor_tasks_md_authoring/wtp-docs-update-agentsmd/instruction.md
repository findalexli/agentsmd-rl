# docs: update AGENTS.md

Source: [satococoa/wtp#83](https://github.com/satococoa/wtp/pull/83)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- align AGENTS.md Go version with go.mod
- include internal/testutil in package list
- clarify WTP_SHELL_INTEGRATION is legacy

## Testing
- not run (docs-only)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
