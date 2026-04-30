# skill(add-gmail-tool): OneCLI-native Gmail MCP tool

Source: [qwibitai/nanoclaw#1961](https://github.com/qwibitai/nanoclaw/pull/1961)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-gmail-tool/SKILL.md`

## What to add / change

## What
Adds \`/add-gmail-tool\` — a Utility skill that installs Gmail as an MCP tool in NanoClaw v2 using OneCLI for credential injection.

## Why
v2's invariant (CHANGELOG 2.0.0) is that containers never receive raw API keys — OneCLI is the sole credential path. No OneCLI-native Gmail skill exists yet. Addresses #1500 on the Gmail side.

## How it works
- Installs [\`@gongrzhe/server-gmail-autoauth-mcp\`](https://github.com/GongRzhe/Gmail-MCP-Server) (pinned) in the container image.
- Allows \`mcp__gmail__*\` in \`TOOL_ALLOWLIST\`.
- Mounts \`~/.gmail-mcp\` (OneCLI-written \`"onecli-managed"\` stubs) into the container per-group via \`container.json\`. The MCP server reads the stubs and calls \`gmail.googleapis.com\`; the OneCLI gateway intercepts and swaps the bearer.
- Pins \`zod-to-json-schema@3.22.5\` alongside the MCP server. The server's loose \`zod: ^3.22.4\` range resolves to \`zod@3.24.x\` while \`zod-to-json-schema@3.25.x\` imports the \`zod/v3\` subpath that only exists in \`zod@>=3.25\` — resulting in \`ERR_PACKAGE_PATH_NOT_EXPORTED\` at startup. Re-check if \`GMAIL_MCP_VERSION\` is bumped.

## How it was tested
End-to-end on Linux + Docker with live OneCLI vault:
- \`gmail-mcp\` spawns cleanly in the rebuilt image; MCP handshake + \`tools/list\` return all 19 tools.
- CLI agent (\`pnpm run chat\`): \"list my gmail labels\" returned real labels.
- WhatsApp self-chat agent: tool calls round-trip through OneCLI with real OAuth bearer injection.
- Verified \`ERR_PA

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
