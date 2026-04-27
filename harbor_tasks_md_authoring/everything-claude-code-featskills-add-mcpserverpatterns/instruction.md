# feat(skills): add mcp-server-patterns

Source: [affaan-m/everything-claude-code#531](https://github.com/affaan-m/everything-claude-code/pull/531)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/mcp-server-patterns/SKILL.md`
- `.cursor/skills/mcp-server-patterns/SKILL.md`
- `skills/mcp-server-patterns/SKILL.md`

## What to add / change

## Summary
Add MCP server patterns skill for building MCP servers (Node/TypeScript SDK, registerTool/registerResource, Zod, stdio vs HTTP).

## Type
- [x] Skill

## Changes
- **skills/mcp-server-patterns/SKILL.md** — Building MCP servers with `@modelcontextprotocol/sdk`; use Context7 or official docs for latest API.

## Checklist
- [x] Follows format guidelines
- [x] No sensitive info
- [x] Clear descriptions

Made with [Cursor](https://cursor.com)

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Added a skill for MCP server patterns to guide building servers with `@modelcontextprotocol/sdk`. Covers tools/resources/prompts, `zod` schemas, version-agnostic stdio guidance, Streamable HTTP, resource handler `uri`, and SDK signature variance across versions with pointers to Context7/official docs; mirrored in `.agents/skills` and `.cursor/skills` for cross-harness use.

- **Bug Fixes**
  - Replaced invalid `StdioServerTransport.create()` example with a version-agnostic note.

<sup>Written for commit 48f2ce812aef55139c268cb3626d0e17540e456e. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added a comprehensive MCP Server Patterns guide covering core concepts (tools, resources, prompts, transports), Node/TypeScript SDK usage with example server setup and tool/resource registrati

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
