# Adopt AGENTS.md convention

Source: [wordpress-mobile/WordPress-iOS#25252](https://github.com/wordpress-mobile/WordPress-iOS/pull/25252)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary

- Rename `CLAUDE.md` → `AGENTS.md` as the source of truth for agent instructions
- New `CLAUDE.md` contains only `@AGENTS.md` pointer

See also:
- bloom/DayOne-Apple#28097
- wordpress-mobile/GutenbergKit#321
- wordpress-mobile/release-toolkit#691
- Automattic/dangermattic#109

---

This PR was created autonomously by Claude Code (Opus 4.6) on behalf of @mokagio with approval.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
