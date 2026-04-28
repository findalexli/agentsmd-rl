# chore: add shadcn skill reminder to frontend AGENTS.md

Source: [bytebase/bytebase#19952](https://github.com/bytebase/bytebase/pull/19952)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `frontend/AGENTS.md`

## What to add / change

## Summary
- Add a note to `frontend/AGENTS.md` reminding AI agents to invoke the `shadcn` skill before writing or modifying React UI components
- Helps agents pick the right component (e.g., `AlertDialog` for confirmations)

## Test plan
- [ ] Verify `frontend/AGENTS.md` renders correctly

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
