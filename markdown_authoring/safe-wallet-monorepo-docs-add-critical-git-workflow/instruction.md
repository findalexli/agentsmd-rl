# docs: Add critical git workflow rules to CLAUDE.md

Source: [safe-global/safe-wallet-monorepo#6909](https://github.com/safe-global/safe-wallet-monorepo/pull/6909)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Added prominent section about never pushing directly to `dev` or `main` branches
- Documented proper feature branch workflow with step-by-step instructions
- Added requirement to always run tests (type-check, lint, test) before committing
- Emphasized that all tests must pass before committing

## Test plan
- [x] Updated CLAUDE.md with new git workflow rules
- [x] Verified formatting with prettier
- [x] Followed the documented workflow by creating this PR on a feature branch

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
