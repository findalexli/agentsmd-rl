# fix: add missing agents and skills to routing-tables.md

Source: [notque/claude-code-toolkit#269](https://github.com/notque/claude-code-toolkit/pull/269)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/do/references/routing-tables.md`

## What to add / change

## Summary
- Add 4 undocumented agents (kotlin, php, swift, research-subagent-executor)
- Add missing skills to appropriate routing table sections
- Remove duplicate go-patterns entry

## Test plan
- [x] Verified all added agents exist on disk
- [x] Verified all added skills have SKILL.md files

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
