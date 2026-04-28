# [copilot] update/simplify instructions

Source: [dotnet/android-libraries#1330](https://github.com/dotnet/android-libraries/pull/1330)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This is an optimized/updated instructions file, about 100 lines shorter.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
