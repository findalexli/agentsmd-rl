# docs: add CLAUDE.md for Claude Code onboarding

Source: [grab/cursor-talk-to-figma-mcp#143](https://github.com/grab/cursor-talk-to-figma-mcp/pull/143)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Adds a `CLAUDE.md` file to help Claude Code (and other AI agents) quickly understand the project architecture, build commands, and development workflow
- Covers the 3-component pipeline (MCP Server, WebSocket Relay, Figma Plugin), key patterns, and local dev setup

## Test plan
- [ ] Verify `CLAUDE.md` renders correctly on GitHub
- [ ] Confirm no existing files were modified

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
