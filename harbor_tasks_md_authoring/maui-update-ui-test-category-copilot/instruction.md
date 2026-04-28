# Update UI test category Copilot instructions

Source: [dotnet/maui#31748](https://github.com/dotnet/maui/pull/31748)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

I've seen Copilot add multiple categories a couple of times now, this will only result in the same test running multiple times which is not useful.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
