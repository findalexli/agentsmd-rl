# feat(skills): add claude-code-sessions productivity skill

Source: [davila7/claude-code-templates#524](https://github.com/davila7/claude-code-templates/pull/524)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `cli-tool/components/skills/productivity/claude-code-sessions/SKILL.md`

## What to add / change

## Summary

- Adds `claude-code-sessions` skill under `productivity/` category
- Session intelligence plugin: search, analyze, and manage Claude Code session history
- 11 skills + web dashboard, zero runtime dependencies, read-only
- GitHub: https://github.com/apappascs/claude-code-sessions

## Details

Claude Code writes JSONL for every session but has no built-in way to search or analyze them. This plugin provides 11 skills usable directly in Claude Code:

- `/session-search` — full-text search across every session
- `/session-stats` — token usage, model distribution, tool breakdown
- `/session-list` — list sessions sorted by recency, size, or duration
- `/session-detail` — deep dive into a specific session
- `/session-diff` — compare two sessions (files, tools, topics)
- `/session-timeline` — chronological view of sessions on a project
- `/session-resume` — generate a context recovery prompt from any session
- `/session-tasks` — find pending and orphaned tasks across sessions
- `/session-export` — export a session as clean markdown
- `/session-cleanup` — find empty, tiny, or stale sessions
- `/session-delete` — delete sessions and their associated tasks

Plus a web dashboard with four views: Dashboard, Sessions, Search, and Tasks.

Same TypeScript modules power skills, dashboard, and CLI. Zero runtime dependencies. Read-only — never writes to Claude Code data.

**Category choice:** `productivity/` — alongside brainstorming, debugger, file-organizer.

## Test plan

- [x] Sk

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
