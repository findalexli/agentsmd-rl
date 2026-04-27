# fix: remove personal preferences from project CLAUDE.md

Source: [rtk-ai/rtk#242](https://github.com/rtk-ai/rtk/pull/242)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Project `CLAUDE.md` is loaded for every contributor using Claude Code on this repo. It currently contains personal preferences that get imposed on all forks and contributors:

- **Hardcoded home directory path** (`/Users/florianbruniaux/Sites/rtk-ai/rtk`) — breaks for every other developer
- **Sibling project references** (`ccboard, cc-economics`) — irrelevant to contributors
- **French language/communication style** (`"User communicates in French"`, `"Bold Guy style"`) — forces all contributors into one person's language preference

These belong in the author's personal `~/.claude/CLAUDE.md`, not in the project's committed `CLAUDE.md`.

## Changes

- Replace hardcoded path with generic `# Verify you're in the rtk project root`
- Remove sibling project names from working directory section
- Remove entire "Language & Communication" section

## Test plan

- [x] No code changes — documentation only
- [x] Verified no other personal preferences remain in CLAUDE.md

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
