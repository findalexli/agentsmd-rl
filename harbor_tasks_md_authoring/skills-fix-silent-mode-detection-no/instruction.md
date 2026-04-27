# fix: silent mode detection, no CLI-broken narration

Source: [heygen-com/skills#54](https://github.com/heygen-com/skills/pull/54)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`
- `heygen-avatar/SKILL.md`
- `heygen-video/SKILL.md`

## What to add / change

## Summary

Ken's OpenClaw agent hit a PATH collision — a Python package had registered `heygen` at `/opt/homebrew/bin/heygen`, which threw `ModuleNotFoundError: No module named 'cli_anything.heygen'`. The agent then narrated the full journey:

> *CLI is broken. Let me check MCP config — README says we just need the MCP server entry...*

Users don't care which transport we use. They care whether the work gets done.

## Fix

Updated API Mode Detection blocks in **SKILL.md**, **heygen-avatar/SKILL.md**, **heygen-video/SKILL.md** with:

1. **New directive:** *"Mode selection is silent. Detect once, pick a mode, move on. Never narrate transport choice ('CLI is broken', 'switching to MCP') — the user doesn't care how calls are made."*

2. **Tightened CLI gate:** *"If MCP tools are not available AND the `heygen` binary runs cleanly (`heygen --version` exits 0), use it. If the CLI is missing, errors on `--version`, or auth is not set, silently skip."*

3. **Single user-facing message only when BOTH fail:** *"To use this skill, connect the HeyGen MCP server or run `heygen auth login` after installing the CLI."*

## Why this works

A bad binary in PATH (like Ken's `cli_anything.heygen` shadow) now fails the `--version` gate and triggers silent skip to MCP, instead of surfacing a cryptic Python traceback to the user.

## Test plan

- [ ] MCP-connected user: agent uses MCP silently, no "detecting mode" narration
- [ ] CLI-only user: agent uses CLI silently
- [ ] Broken `heygen` binary i

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
