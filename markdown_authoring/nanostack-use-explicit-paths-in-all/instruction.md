# Use explicit paths in all SKILL.md and simplify script resolution

Source: [garagon/nanostack#65](https://github.com/garagon/nanostack/pull/65)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`
- `compound/SKILL.md`
- `plan/SKILL.md`
- `qa/SKILL.md`
- `review/SKILL.md`
- `security/SKILL.md`
- `ship/SKILL.md`
- `think/SKILL.md`

## What to add / change

## Summary

Artifacts were not being saved during sprints. Root cause: the Script Resolution section in SKILL.md used a complex dynamic path resolution that failed silently, and the fallback instruction said "skip the script call and proceed." The agent resolved nothing, saved nothing.

Fix: every script call in every SKILL.md now uses `~/.claude/skills/nanostack/bin/` directly. The root SKILL.md states that saving artifacts is not optional.

## Test plan

- [x] All script calls use explicit `~/.claude/skills/nanostack/bin/` path
- [x] No "skip if missing" fallback — saving is mandatory
- [x] Root SKILL.md simplified to 4 lines instead of 10

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
