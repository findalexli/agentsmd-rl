# refactor: decompose reddit-moderate SKILL.md into references

Source: [notque/claude-code-toolkit#428](https://github.com/notque/claude-code-toolkit/pull/428)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/reddit-moderate/SKILL.md`
- `skills/reddit-moderate/references/classification-prompt.md`
- `skills/reddit-moderate/references/context-loading.md`
- `skills/reddit-moderate/references/script-commands.md`

## What to add / change

## Summary
- Decomposed reddit-moderate SKILL.md from 403 lines to 166 lines
- Created 3 reference files: classification-prompt.md, script-commands.md, context-loading.md
- All 5 workflow phases (FETCH/CLASSIFY/PRESENT/CONFIRM/ACT) preserved in SKILL.md
- Only content catalogs (prompt template, command reference, config spec) moved to references

## Test plan
- [ ] All 5 workflow phases present in SKILL.md
- [ ] Classification prompt template preserved in references
- [ ] Script command reference preserved
- [ ] Ruff lint passes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
