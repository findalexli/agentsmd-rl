# Adding AGENTS.md files for root and unit test folders

Source: [microsoft/vscode-mssql#20269](https://github.com/microsoft/vscode-mssql/pull/20269)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `test/unit/AGENTS.md`

## What to add / change

I've been using a variation on this unit test prompt for converting old TypeMoq unit tests.

Root file is copilot-generated, from https://github.com/microsoft/vscode-mssql/pull/19996

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
