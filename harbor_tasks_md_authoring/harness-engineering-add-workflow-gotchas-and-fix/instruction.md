# Add workflow gotchas and fix stale commands in CLAUDE.md

Source: [jrenaldi79/harness-engineering#17](https://github.com/jrenaldi79/harness-engineering/pull/17)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

- 5 new Critical Gotchas from session learnings: two generate-docs scripts, two setup code paths, squash-merge branch hygiene, auto-doc commit behavior
- Fixed stale test commands (node_modules/.bin/jest -> npx jest)
- Added to Code Review Checklist: skill change = eval change, eval dry-run after infra changes

## Test plan

- [ ] CLAUDE.md under 300 lines
- [ ] Pre-commit hook auto-updates AUTO markers

https://claude.ai/code/session_01Hbxy31TkbujzukGFSxLcPw

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
