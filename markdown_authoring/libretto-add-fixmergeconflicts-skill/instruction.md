# Add fix-merge-conflicts skill

Source: [saffron-health/libretto#39](https://github.com/saffron-health/libretto/pull/39)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/fix-merge-conflicts/SKILL.md`

## What to add / change

## Summary
- add a new `fix-merge-conflicts` skill at `.agents/skills/fix-merge-conflicts/SKILL.md`
- resolve conflicts by preserving intent from associated PR title/description
- require a user-intervention checkpoint whenever intents diverge

## Notes
- keep existing unrelated local edits out of this PR

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
