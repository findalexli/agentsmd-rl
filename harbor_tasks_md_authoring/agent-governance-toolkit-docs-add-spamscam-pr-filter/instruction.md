# docs: add spam/scam PR filter to copilot instructions

Source: [microsoft/agent-governance-toolkit#1313](https://github.com/microsoft/agent-governance-toolkit/pull/1313)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Add rules to auto-close promotional/spam PRs and issues.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
