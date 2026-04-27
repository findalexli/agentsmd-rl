# Revert to relative bin/ paths that worked in production

Source: [garagon/nanostack#67](https://github.com/garagon/nanostack/pull/67)

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

Root cause found: absolute paths (`~/.claude/skills/nanostack/bin/save-artifact.sh`) don't match Claude Code's Bash permission patterns. The full path as first token of a command doesn't match `Bash(mkdir:*)` style patterns. The agent silently skips execution.

Relative paths (`bin/save-artifact.sh`) worked in the world clock sprint (PR #58 era) because Claude Code resolves them from the skill installation directory, not the user's pwd.

Reverted all 7 SKILL.md files to relative `bin/` paths and removed the Script Resolution section entirely.

## Evidence

- World clock sprint (commit a64122f): relative paths, artifacts saved correctly
- All sprints after PR #63/#65: absolute paths, zero artifacts saved
- Permission `Bash(~/.claude/skills/nanostack/bin/*:*)` did not help

## Test plan

- [x] Zero absolute paths in any SKILL.md
- [x] Script Resolution section removed from root SKILL.md
- [x] "Saving artifacts is not optional" statement preserved

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
