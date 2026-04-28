# Expose MCP skills via .well-known/agent-skills/ discovery

Source: [modelcontextprotocol/modelcontextprotocol#2589](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2589)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `docs/.mintlify/skills/search-mcp-github/SKILL.md`
- `plugins/mcp-spec/skills/search-mcp-github/SKILL.md`

## What to add / change

Adds `.mintlify/skills/` with a symlink to the `search-mcp-github` skill so it's auto-served at `/.well-known/agent-skills/index.json`. Also adds `license: Apache-2.0` to the skill frontmatter per the agentskills.io spec.

Mintlify documentation: https://www.mintlify.com/docs/ai/skillmd#custom-skill-files

🦉 Generated with [Claude Code](https://claude.ai/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
