# docs: adding Copilot instructions

Source: [rugk/awesome-emoji-picker#160](https://github.com/rugk/awesome-emoji-picker/pull/160)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

I accidentially pressed the wrong button and had VSCode/Copilot generate this file for… itself. :D

Maybe it is useful, so maybe we can commit it. I skimmed it and fixed some minor hallucinations, otherwise it seems to be correct.

see https://code.visualstudio.com/docs/copilot/copilot-customization

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
