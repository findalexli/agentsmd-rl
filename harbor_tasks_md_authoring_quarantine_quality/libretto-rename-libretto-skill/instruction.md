# Rename libretto skill

Source: [saffron-health/libretto#41](https://github.com/saffron-health/libretto/pull/41)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/libretto/SKILL.md`
- `.agents/skills/push/SKILL.md`
- `packages/libretto/skill/SKILL.md`

## What to add / change

## Summary
- rename the `packages/libretto/skill` skill from `libretto-network-skill` to `libretto`
- run `pnpm i` to sync the generated skill copy in `.agents/skills/libretto/SKILL.md`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
