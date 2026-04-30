# [SAB-94] Refactor: split and localize .claude/rules

Source: [riii111/sabiql#196](https://github.com/riii111/sabiql/pull/196)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/app-state.md`
- `.claude/rules/architecture.md`
- `.claude/rules/config-migration.md`
- `.claude/rules/db-agnostic.md`
- `.claude/rules/interaction-contract.md`
- `.claude/rules/postgres-adapter.md`
- `.claude/rules/rendering-strategy.md`
- `.claude/rules/rstest-patterns.md`
- `.claude/rules/rust-testing-style.md`
- `.claude/rules/test-organization.md`
- `.claude/rules/testing-obligations.md`
- `.claude/rules/ui-design.md`
- `.claude/rules/visual-regression.md`
- `CLAUDE.md`

## What to add / change

## Scope

`.claude/rules/` and `CLAUDE.md` only. No application code changes.

## Summary

- Split large rules (`architecture.md`, `rust-testing-style.md`) into path-scoped sub-rules to reduce context window load
- Remove duplicate content across rules
- Localize all rules from English to Japanese for maintainability
- Remove redundant auto-fire skills — content already covered by rules
- Update `CLAUDE.md` rules table

## Metrics

| Metric | Before | After |
|--------|--------|-------|
| Context loaded on all `.rs` files | ~321 lines | ~140 lines |
| Rule files | 8 | 13 (5 new path-scoped) |
| Auto-fire skills | 4 | 0 |

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
