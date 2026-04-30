# chore(copilot-instructions): update communication with standardized conventions

Source: [Esri/calcite-design-system#14322](https://github.com/Esri/calcite-design-system/pull/14322)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

**Related Issue:** #

## Summary
The previous markup had no effect on Copilot's review formatting.

Updates the repository’s Copilot/review communication guidance to use standardized, explicit labels for review comment intent and severity.

**Changes:**
- Replaces the generic “label the type of review comment” guidance with a standardized `<label>:` prefix format.
- Defines a recommended set of labels (`blocking:`, `suggestion:`, `nit:`, `question:`) and what each means.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
