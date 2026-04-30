# chore: remove cursor-specific rules in favor of skills and AGENTS.md

Source: [inkeep/agents#1717](https://github.com/inkeep/agents/pull/1717)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/adding-documentation.mdc`
- `.cursor/rules/test-no-watch.mdc`
- `.cursor/rules/use-pnpm.mdc`

## What to add / change

## Summary
- Remove redundant cursor-specific rule files that are now covered by AGENTS.md and skills
- Deleted `.cursor/rules/adding-documentation.mdc`, `.cursor/rules/test-no-watch.mdc`, `.cursor/rules/use-pnpm.mdc`

## Test plan
- [x] No functional code changes, just removal of config files

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
