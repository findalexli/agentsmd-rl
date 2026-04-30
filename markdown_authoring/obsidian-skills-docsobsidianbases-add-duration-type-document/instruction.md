# docs(obsidian-bases): add Duration type documentation and fix date formulas

Source: [kepano/obsidian-skills#35](https://github.com/kepano/obsidian-skills/pull/35)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/obsidian-bases/SKILL.md`

## What to add / change

## Summary
- Add comprehensive Duration type documentation with fields (.days, .hours, etc.)
- Fix date calculation formulas to use .days property instead of millisecond division
- Clarify that Duration type doesn't support direct .round() calls
- Add correct/incorrect examples for date arithmetic

## Test plan
- [x] Verify documentation accuracy against Obsidian Bases behavior
- [x] Test example formulas in an actual Obsidian vault

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
