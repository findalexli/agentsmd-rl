# Add copilot instructions

Source: [microsoft/winget-cli#6048](https://github.com/microsoft/winget-cli/pull/6048)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Written largely by CoPilot itself.
 ###### Microsoft Reviewers: [Open in CodeFlow](https://microsoft.github.io/open-pr/?codeflow=https://github.com/microsoft/winget-cli/pull/6048)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
