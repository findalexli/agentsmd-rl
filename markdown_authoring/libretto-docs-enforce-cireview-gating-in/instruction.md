# docs: enforce CI/review gating in push skill

Source: [saffron-health/libretto#36](https://github.com/saffron-health/libretto/pull/36)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/push/SKILL.md`

## What to add / change

## Summary
- rename commit section to "Commit and PR workflow"
- add CI and AI review bot gating guidance to the `push` skill
- keep existing PR body formatting guidance intact

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
