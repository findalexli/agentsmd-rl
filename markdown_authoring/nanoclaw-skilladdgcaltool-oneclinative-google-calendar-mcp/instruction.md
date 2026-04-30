# skill(add-gcal-tool): OneCLI-native Google Calendar MCP tool

Source: [qwibitai/nanoclaw#1964](https://github.com/qwibitai/nanoclaw/pull/1964)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-gcal-tool/SKILL.md`

## What to add / change

## What
Adds `/add-gcal-tool` — a sibling to `/add-gmail-tool` (#1961) that installs Google Calendar as an MCP tool using OneCLI for credential injection.

## Why
Calendar is the obvious companion to Gmail for personal-assistant workflows ("am I free tomorrow at 2?", "put X on my calendar"). Reusing the stub pattern + allowlist conventions established by `/add-gmail-tool` keeps both installations consistent.

## How it works
- Installs [`@gongrzhe/server-calendar-autoauth-mcp@1.0.2`](https://github.com/GongRzhe/Google-Calendar-MCP-Server) (pinned) in the container image, alongside the gmail MCP in the existing pnpm global-install block.
- Allows `mcp__calendar__*` in `TOOL_ALLOWLIST`.
- Per-group: mounts `~/.calendar-mcp` (OneCLI-written `"onecli-managed"` stubs) into `/workspace/extra/.calendar-mcp`. The MCP server reads the stubs and calls `calendar.googleapis.com`; OneCLI swaps the bearer.
- Reuses the `zod-to-json-schema@3.22.5` pin from #1961 — calendar-mcp has the same loose `zod: ^3.24.1` + `zod-to-json-schema: ^3.22.4` deps that resolve to an `ERR_PACKAGE_PATH_NOT_EXPORTED` crash on startup without the pin.

## Depends on
**#1961** (add-gmail-tool) — introduces the shared pnpm install block and the `zod-to-json-schema` pin. If #1961 merges first, the diff against main is the single calendar commit (3 files, +208). If #1961 closes, this PR can be rebased to add its own standalone install block (the SKILL.md already documents both orderings in Phase 2).

## How it was t

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
