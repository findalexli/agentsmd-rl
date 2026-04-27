# fix(SKILL): HEYGEN_API_KEY presence → use CLI, short-circuit MCP

Source: [heygen-com/skills#60](https://github.com/heygen-com/skills/pull/60)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Problem

Current detection order: MCP preferred → CLI fallback. If both are configured (MCP connected AND `HEYGEN_API_KEY` set), MCP wins silently. That's wrong: an explicit API key is an explicit user signal — they want direct API access, not OAuth.

Net effect: users who followed the CLI install path (API key in env) get silently routed through MCP if an MCP server happens to be present. Surprising, and it defeats the whole point of setting a key.

## Fix

New 4-level priority:

1. **CLI mode (API-key override)** — `HEYGEN_API_KEY` set AND `heygen --version` exits 0 → use CLI. Short-circuits MCP detection.
2. **MCP mode** — no key AND `mcp__heygen__*` tools visible → use MCP (OAuth, plan credits).
3. **CLI mode (fallback)** — no key AND no MCP AND `heygen --version` exits 0 → use CLI with `heygen auth login`.
4. **Neither** — tell the user how to connect.

## Scope

- Single edit to root `SKILL.md` (+5 -4 lines)
- Prompt-only, no API/behavioral changes

Related: #59

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
