# Align Patrol test rules across Claude skills and Cursor rules

Source: [leancodepl/patrol#3033](https://github.com/leancodepl/patrol/pull/3033)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/patrol-tests-architecture/SKILL.md`
- `.claude/skills/patrol-tests/SKILL.md`
- `.cursor/rules/patrol-test-with-architecture/patrol-test-keys.mdc`
- `.cursor/rules/patrol-test-with-architecture/patrol-tests.mdc`
- `.cursor/rules/patrol-test/patrol-tests.mdc`

## What to add / change

Sync the basic and architecture Patrol rules between .claude/skills and .cursor/rules so the same guidance applies in both tools.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
