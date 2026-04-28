# Update CLAUDE.md

Source: [ArcadeAI/arcade-mcp#815](https://github.com/ArcadeAI/arcade-mcp/pull/815)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

<!-- CURSOR_SUMMARY -->
> [!NOTE]
> **Low Risk**
> Documentation-only changes that clarify protocols, CLI usage, and environment/configuration conventions; no runtime behavior or dependencies are modified.
> 
> **Overview**
> **Updates `CLAUDE.md` from a brief repo note to a comprehensive developer guide.** It now documents the dual-protocol HTTP server model (MCP + Arcade Worker), key runtime components (`MCPApp`, transports, context, middleware), and how tool discovery, auth/secrets, and error handling are intended to work.
> 
> Also refreshes contributor workflow guidance: updated `make`/`uv` commands, CLI command overview, key environment variables, test/fixture locations, and stricter notes about avoiding stdout/stderr pollution in stdio transport paths.
> 
> <sup>Reviewed by [Cursor Bugbot](https://cursor.com/bugbot) for commit 2e08a62e22f02d4531fdcf6a73837aa8dd38607f. Bugbot is set up for automated code reviews on this repo. Configure [here](https://www.cursor.com/dashboard/bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
