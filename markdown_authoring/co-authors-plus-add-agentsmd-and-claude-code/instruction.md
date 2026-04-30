# Add AGENTS.md and Claude Code config

Source: [Automattic/co-authors-plus#1207](https://github.com/Automattic/co-authors-plus/pull/1207)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`
- `AGENTS.md`

## What to add / change

## Summary

- Adds `AGENTS.md` with AI agent context for the co-authors-plus plugin, covering taxonomy-based architecture, guest authors, commands, conventions, and common pitfalls
- Adds `.claude/CLAUDE.md` referencing `AGENTS.md`

This aligns co-authors-plus with the other 14 plugins that already have these files, giving AI coding assistants the project context they need to work effectively.

## Test plan

- [ ] Verify `AGENTS.md` content accurately reflects the plugin structure
- [ ] Confirm no functional changes — documentation only

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
