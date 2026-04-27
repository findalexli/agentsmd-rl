# fix: disambiguate 3 high-risk semantic overlap clusters

Source: [liqiongyu/lenny_skills_plus#17](https://github.com/liqiongyu/lenny_skills_plus/pull/17)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/cross-functional-collaboration/SKILL.md`
- `skills/evaluating-trade-offs/SKILL.md`
- `skills/managing-up/SKILL.md`
- `skills/running-decision-processes/SKILL.md`
- `skills/stakeholder-alignment/SKILL.md`
- `skills/systems-thinking/SKILL.md`

## What to add / change

## Summary
Add `NOT for` cross-references and sharpen trigger keywords to prevent mis-triggering between 6 confusable skills across 3 overlap clusters:

- **"build vs buy"**: `evaluating-new-technology` owns it; `evaluating-trade-offs` defers for technology/vendor decisions
- **"decision"**: `running-decision-processes` (process facilitation), `evaluating-trade-offs` (analytical comparison), `systems-thinking` (systemic effects) now have clear boundaries
- **"stakeholder"**: `stakeholder-alignment` (one-time buy-in), `cross-functional-collaboration` (ongoing operating model), `managing-up` (boss relationship) explicitly exclude each other

## Test plan
- [x] `python3 scripts/ci_check_skillpacks.py --skip-mirror-check` — 87/87 pass
- [x] All descriptions under 500 char limit

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
