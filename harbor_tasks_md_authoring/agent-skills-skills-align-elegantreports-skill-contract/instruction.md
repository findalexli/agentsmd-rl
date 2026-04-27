# skills: align elegant-reports skill contract with scanner

Source: [jdrhyne/agent-skills#18](https://github.com/jdrhyne/agent-skills/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/elegant-reports/SKILL.md`

## What to add / change

## Summary
- align `skills/elegant-reports/SKILL.md` with the skill's real execution contract
- add explicit permission declarations and safety boundaries
- remove scanner-confusing patterns that were inflating trust findings

## Validation
- `npm test`
- live AgentVerus paste-scan of the revised `SKILL.md`
  - before: 95 / CONDITIONAL / 7 findings
  - after: 99 / CERTIFIED / 3 findings

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
