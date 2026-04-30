# docs: enhance CLAUDE.md with comprehensive architecture overview

Source: [anthropics/claude-code-action#362](https://github.com/anthropics/claude-code-action/pull/362)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Enhanced CLAUDE.md with detailed two-phase execution architecture documentation
- Added comprehensive breakdown of mode system (tag/agent) and GitHub integration layers
- Documented MCP server architecture, authentication flow, and branching strategies
- Included complete project structure with component descriptions and code conventions

## Test plan
- [x] Verify CLAUDE.md formatting and structure
- [x] Ensure all architectural components are accurately documented
- [x] Confirm development commands and conventions are complete

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
