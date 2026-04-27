# feat(skill): compound planning — incremental reports, agent routing, improvement hook

Source: [backnotprop/plannotator#455](https://github.com/backnotprop/plannotator/pull/455)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `apps/skills/plannotator-compound/SKILL.md`

## What to add / change

## Summary
- **Incremental reports**: Detects previous reports, offers to only analyze new files since last report (saves tokens). Output filenames are versioned (`-v2`, `-v3`, etc.)
- **Haiku/Sonnet agent routing**: Extraction (Phase 2) uses Haiku agents for speed; reduction (Phase 3) uses Sonnet for analytical reasoning, with two-stage reduce for large datasets
- **Improvement hook (Phase 6)**: After the report, offers to write corrective prompt instructions to `~/.plannotator/compound/enterplanmode-improve-hook.txt` for automatic injection into future planning sessions. Handles existing hooks with replace/merge/keep options

## Test plan
- [ ] Run skill with no previous report — should produce `compound-planning-report.html` (no version suffix)
- [ ] Run skill again — should detect previous report, offer incremental vs full, output as `-v2`
- [ ] Verify incremental mode filters files by cutoff date
- [ ] Verify Phase 6 creates the improvement hook file
- [ ] Run again to verify existing hook reconciliation (replace/merge/keep)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
