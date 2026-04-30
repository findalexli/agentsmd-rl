# Create copilot-instructions.md for makefile tools

Source: [microsoft/vscode-makefile-tools#805](https://github.com/microsoft/vscode-makefile-tools/pull/805)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

see title. most of it was based off of cmake tools

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
