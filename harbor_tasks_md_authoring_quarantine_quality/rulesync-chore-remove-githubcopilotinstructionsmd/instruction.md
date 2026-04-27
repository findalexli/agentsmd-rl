# chore: remove .github/copilot-instructions.md

Source: [dyoshikawa/rulesync#1457](https://github.com/dyoshikawa/rulesync/pull/1457)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Summary
- Remove `.github/copilot-instructions.md` as it is no longer needed
- Project instructions are already managed through `CLAUDE.md` and rulesync configuration files

## Test plan
- [x] `pnpm cicheck` passes (all code and content checks green)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
