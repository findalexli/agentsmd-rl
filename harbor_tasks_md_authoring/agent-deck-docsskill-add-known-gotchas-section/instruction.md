# docs(skill): add Known Gotchas section to agent-deck skill

Source: [asheshgoplani/agent-deck#621](https://github.com/asheshgoplani/agent-deck/pull/621)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/agent-deck/SKILL.md`

## What to add / change

## Summary

Appends a "Known Gotchas (v1.7.0+)" section to the agent-deck skill — a canonical list of friction points discovered during real usage, each with a tested workaround.

All content is generic (placeholder-based: `<profile>`, `<id>`, `<mac-user>` etc.) so it applies to any agent-deck user regardless of their specific setup.

## Contents

1. **`session send --no-wait` buffering** — prompts typed but not submitted on freshly-launched sessions; `tmux send-keys Enter` workaround.
2. **Binary text-busy replacement** — move-then-copy pattern for hot-reloading the agent-deck binary while tmux sessions are running.
3. **Cross-machine `sources.toml` path drift** — macOS `/Users/` paths don't work on Linux; `sed` fix.
4. **Channel subscription (v1.7.0+)** — proper use of `--channel` / `session set channels` for conductor/bot sessions that need Telegram/Discord/Slack inbound as conversation turns.
5. **Competing telegram pollers race** — exactly one session should load the telegram channel plugin; disable globally and enable per-session.

## Context

Each gotcha represents a multi-hour debugging session that ended with a one-line workaround. Having them in the skill means future `agent-deck` users hit them, grep the skill, find the answer in seconds.

Observed during dogfood of the `claude-conductor` skill (which also lives in the pool but is conductor-local — this is the user-facing skill, strictly generic).

## Test plan

Docs-only. No code change, no tests needed.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
