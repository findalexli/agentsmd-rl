# Reduce SKILL.md tokens by 14% (-2,203 tokens per sprint)

Source: [garagon/nanostack#82](https://github.com/garagon/nanostack/pull/82)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `qa/SKILL.md`
- `security/SKILL.md`
- `ship/SKILL.md`
- `think/SKILL.md`

## What to add / change

## Summary
Aggressive token reduction across 4 skills without losing behavior:

| Skill | Before | After | Savings |
|-------|--------|-------|---------|
| think | 2,083 | 1,353 | -35% |
| security | 2,043 | 1,693 | -17% |
| qa | 1,854 | 1,683 | -9% |
| ship | 1,772 | 1,328 | -25% |
| **Sprint total** | **15,973 tokens** | **13,769 tokens** | **-14%** |

## What was cut
- Inline tables replaced with reference file pointers (think forcing questions, STRIDE)
- Verbose gotchas/anti-patterns condensed (ship: 17 items → 4)
- Obvious behavior removed (prompt injection 11 lines → 3, WTF heuristic 15 lines → 2)
- Deploy walkthrough moved inline (25 lines → 3)
- Severity classification table → one line

## What was NOT cut
- Process steps, phase transitions, artifact save instructions
- Reference file content (stays the same, loaded on demand)
- Mode selection logic, scope drift, conflict detection

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
