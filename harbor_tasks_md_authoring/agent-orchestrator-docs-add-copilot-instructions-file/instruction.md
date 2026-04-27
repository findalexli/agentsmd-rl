# docs: add Copilot instructions file

Source: [ComposioHQ/agent-orchestrator#1331](https://github.com/ComposioHQ/agent-orchestrator/pull/1331)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Summary
- add .github/copilot-instructions.md from the AO draft
- preserve the original guidance while cleaning up grammar, wording, and markdown formatting
- fix malformed code fences and examples so the file reads cleanly on GitHub

## Testing
- not run by request; markdown-only change

## Notes
- no tracker issue number was provided for this task.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
