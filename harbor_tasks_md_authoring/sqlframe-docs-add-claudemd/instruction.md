# docs: add CLAUDE.md

Source: [eakmanrq/sqlframe#596](https://github.com/eakmanrq/sqlframe/pull/596)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add CLAUDE.md with development commands (install, test, lint, style), single test execution examples, and high-level architecture overview
- Covers key patterns: generics, mixins, dialect structure, functions system, operation/CTE tracking

## Test plan
- [x] `make style` passes
- No code changes, documentation only

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
