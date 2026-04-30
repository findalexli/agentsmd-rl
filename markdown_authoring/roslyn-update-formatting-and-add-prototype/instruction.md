# Update formatting and add PROTOTYPE comments note in copilot-instructions

Source: [dotnet/roslyn#80677](https://github.com/dotnet/roslyn/pull/80677)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Added to fix https://github.com/dotnet/roslyn/pull/80617#discussion_r2426720483

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
