# Add AGENTS.md contributor guide

Source: [IfcOpenShell/IfcOpenShell#7672](https://github.com/IfcOpenShell/IfcOpenShell/pull/7672)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

AI agents are supposed to read repository specific instructions from a file called AGENTS.md in the root of the project folder whenever they work on the repository.

This commit contains guidelines for external contributors using AI coding tools, covering licensing, AI disclosure requirements, PR scope, commit style, code formatting, and testing expectations.

Assuming that generated contributions are acceptable - and this is a matter for discussion @aothms @Moult @Andrej730 @falken10vdl @theoryshaw - this is one way to deal with this.

Generated with the assistance of an AI coding tool.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
