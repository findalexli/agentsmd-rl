# refactor: decompose php-quality SKILL.md into references

Source: [notque/claude-code-toolkit#425](https://github.com/notque/claude-code-toolkit/pull/425)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/php-quality/SKILL.md`
- `skills/php-quality/references/framework-idioms.md`
- `skills/php-quality/references/modern-php-features.md`
- `skills/php-quality/references/quality-tools.md`

## What to add / change

## Summary
- Decomposed php-quality SKILL.md from 351 lines to 88 lines
- Created 3 reference files: modern-php-features.md, framework-idioms.md, quality-tools.md
- Added ASSESS/REVIEW phase workflow to thin orchestrator
- Validated: 23/23 content sections preserved, reference tests pass

## Test plan
- [ ] All PHP features, framework idioms, and tool configs preserved
- [ ] validate-references.py passes
- [ ] Ruff lint passes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
