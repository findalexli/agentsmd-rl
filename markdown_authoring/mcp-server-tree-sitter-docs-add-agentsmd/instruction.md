# docs: add AGENTS.md

Source: [wrale/mcp-server-tree-sitter#40](https://github.com/wrale/mcp-server-tree-sitter/pull/40)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
Adds AGENTS.md with instructions for AI coding agents working in this repo. Covers:

- Setup and CI requirements
- Key architecture and file layout
- tree-sitter API compat rules (use `query_captures` wrapper)
- How to add new languages
- Common pitfalls (circular imports, root logger, TypeScript grammar)
- PR and release process

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
