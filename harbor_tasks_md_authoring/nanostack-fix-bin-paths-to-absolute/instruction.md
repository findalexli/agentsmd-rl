# Fix bin/ paths to absolute skill root in all SKILL.md

Source: [garagon/nanostack#63](https://github.com/garagon/nanostack/pull/63)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary

All SKILL.md files referenced scripts as `bin/save-artifact.sh` (relative path). When the agent runs from a user project directory (e.g. `~/projects/myapp/`), the path resolves to `~/projects/myapp/bin/save-artifact.sh` which doesn't exist. The agent then skips artifact saving entirely.

Changed all 8 SKILL.md files to use `~/.claude/skills/nanostack/bin/` so scripts resolve correctly from any working directory.

Discovered during live testing: agent reported "No artifact script found — skipping artifact save" because it couldn't resolve the relative path from the project directory.

## Test plan

- [x] Zero relative `bin/` paths remain in any SKILL.md
- [x] All 38 script references now use `~/.claude/skills/nanostack/bin/`
- [x] Grep confirms no stale relative paths

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
