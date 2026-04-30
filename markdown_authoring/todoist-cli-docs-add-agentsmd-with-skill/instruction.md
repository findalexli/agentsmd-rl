# docs: add AGENTS.md with skill content sync instructions

Source: [Doist/todoist-cli#48](https://github.com/Doist/todoist-cli/pull/48)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary
- Move all project guidelines from `CLAUDE.md` to `AGENTS.md` so they're agent-agnostic
- Add new "Skill Content" section documenting the contract to keep `SKILL_CONTENT` in `src/lib/skills/content.ts` in sync when commands/flags/options change
- Replace `CLAUDE.md` with a pointer to `AGENTS.md`

## Test plan
- [x] `AGENTS.md` contains all previous CLAUDE.md content plus new skill-update instructions
- [x] `CLAUDE.md` is a single-line pointer to AGENTS.md
- [x] All existing tests pass (668/668)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
