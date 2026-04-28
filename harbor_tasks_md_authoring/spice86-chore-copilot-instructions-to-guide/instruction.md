# chore: copilot instructions to guide it

Source: [OpenRakis/Spice86#1403](https://github.com/OpenRakis/Spice86/pull/1403)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

### Description of Changes

A file to guide copilot when in agent mode or ask mode.

Automatically used with VSCode, has to be included manually in VS.

### Rationale behind Changes

Hopefully copilot will be less silly

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
