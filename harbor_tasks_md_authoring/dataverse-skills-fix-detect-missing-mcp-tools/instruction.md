# fix: detect missing MCP tools and route to mcp-configure instead of silent SDK fallback

Source: [microsoft/Dataverse-skills#12](https://github.com/microsoft/Dataverse-skills/pull/12)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/plugins/dataverse/skills/init/SKILL.md`
- `.github/plugins/dataverse/skills/mcp-configure/SKILL.md`
- `.github/plugins/dataverse/skills/overview/SKILL.md`

## What to add / change

## Problem

When a user says 'Connect via MCP to our Dataverse environment', the agent detects that MCP tools aren't available but **silently falls back to the Python SDK** instead of configuring MCP. The user cancelled after 3.5 minutes of watching the agent write a Python script they didn't ask for.

### Root cause: 3 missing links

1. **Overview skill** had no 'MCP Availability Check' - after detecting MCP tools were missing, the agent had no guidance to load `mcp-configure`
2. **Init skill** MCP skip logic was too aggressive - skipped MCP setup even when user explicitly asked for MCP
3. **mcp-configure** trigger phrases only matched explicit setup intent ('configure MCP', 'set up MCP server') - missed operational phrases like 'connect via MCP'

## Solution

### overview/SKILL.md
- Added **MCP Availability Check** section after Tool Capabilities table: if MCP tools aren't in the tool list and the user wants MCP, do NOT silently fall back - load `dataverse-mcp-configure` instead
- Updated 'When in doubt' guidance to start with MCP availability check

### init/SKILL.md
- Added exception to MCP skip conditions in both Scenario A (step 8) and Scenario B (step 11): 'do NOT skip if user explicitly mentioned MCP or asked to connect via MCP'

### mcp-configure/SKILL.md
- Added operational trigger phrases: 'connect via MCP', 'use MCP', 'MCP tools not available', 'no MCP tools', 'MCP not configured'

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
