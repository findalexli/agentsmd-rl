# Document the release process in CLAUDE.md

Source: [shader-slang/slang#10903](https://github.com/shader-slang/slang/pull/10903)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/slang-release-process/SKILL.md`
- `CLAUDE.md`

## What to add / change

## Summary
- Add a "Release Process" section to CLAUDE.md covering the end-to-end release workflow
- Documents prerequisites (gh CLI install, `read:project` token scope)
- Steps: trigger Release CI, determine version from sprint number (including a GraphQL query to look up the current sprint programmatically), generate release notes, create and push the annotated tag
- Includes tag naming conventions for sprints, hotfixes, and respins

## Test plan
- [x] Verified the GraphQL query works with `read:project` scope
- [x] Verified the sprint-to-version formula against existing release tags
- [x] Successfully used this process to ship v2026.7

Made with [Cursor](https://cursor.com)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
