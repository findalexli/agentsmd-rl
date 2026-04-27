# Wire cross-skill artifact reading for flow optimization

Source: [garagon/nanostack#24](https://github.com/garagon/nanostack/pull/24)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plan/SKILL.md`
- `qa/SKILL.md`
- `review/SKILL.md`
- `security/SKILL.md`
- `ship/SKILL.md`

## What to add / change

## Summary

Skills now read each other's artifacts. Before this change, 88% of data produced was never consumed.

| Metric | Before | After | Improvement |
|---|---|---|---|
| Handoff utilization | 12% | 37% | +208% |
| Artifact field utilization | 5% | 38% | +660% |
| Cross-reference coverage | 33% | 89% | +170% |

Changes:
- /nano reads /think artifact (key_risk, narrowest_wedge, scope_mode, premise_validated)
- /review reads plan.risks[] for risk-focused adversarial pass
- /review reads plan.out_of_scope[] to detect scope creep
- /security reads planned_files and risks to focus the audit
- /qa reads product standards from plan for visual QA analysis
- /ship verifies blocking review findings were resolved

## Test plan

- [ ] Run /nano after /think and verify it references think artifact data
- [ ] Run /review and verify it creates a risk checklist from plan.risks[]
- [ ] Run /ship and verify it checks for unresolved blocking findings

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
