# fix: wrong filename when referring `archive-....mdc` in `archive-mode-map.mdc`

Source: [vanzan01/cursor-memory-bank#41](https://github.com/vanzan01/cursor-memory-bank/pull/41)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/isolation_rules/visual-maps/archive-mode-map.mdc`

## What to add / change

This pull request updates the archive mode map in `.cursor/rules/isolation_rules/visual-maps/archive-mode-map.mdc` to improve the accuracy and consistency of the archiving level references. The main changes are focused on updating the file names and display text for each complexity level in the visual map.

**Visual map updates:**
* Updated the display text and linked file names for each archiving level:
  - Level 1 now omits the file name reference.
  - Level 2 now references `Level2/archive-basic.mdc` instead of `.md`.
  - Level 3 now references `Level3/archive-intermediate.mdc` instead of `archive-standard.md`.
  - Level 4 now references `Level4/archive-comprehensive.mdc` instead of `.md`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
