# Simplify copilot instructions

Source: [dotnet/razor#12870](https://github.com/dotnet/razor/pull/12870)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

While in a meeting where it was suggested to tell copilot to review and simplify the copilot-instructions file, I got copilot to review and simplify the copilot-instructions file.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
