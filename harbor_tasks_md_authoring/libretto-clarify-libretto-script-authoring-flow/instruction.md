# Clarify Libretto script authoring flow

Source: [saffron-health/libretto#105](https://github.com/saffron-health/libretto/pull/105)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/libretto/SKILL.md`
- `.claude/skills/libretto/SKILL.md`
- `skills/libretto/SKILL.md`

## What to add / change

## Summary
- update the Libretto skill description to frame Libretto as a script-authoring CLI
- require new automation and scrape tasks to produce a workflow file before the task is considered complete
- sync the same guidance into the mirrored Codex and Claude skill copies

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
