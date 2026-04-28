# docs: improve CLAUDE.md monorepo structure documentation

Source: [liam-hq/liam#3712](https://github.com/liam-hq/liam/pull/3712)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Issue

- resolve: N/A (documentation improvement)

## Why is this change needed?

The existing CLAUDE.md file had some inconsistencies and missing information:

1. **Missing package documentation**: The `@liam-hq/agent` package was referenced in the App-specific Commands section but wasn't documented in the Monorepo Structure section
2. **Unclear package organization**: No distinction between public packages (in `frontend/packages/`) and internal packages (in `frontend/internal-packages/`)
3. **Missing LangGraph reference**: No pointer to the comprehensive LangGraph documentation in `docs/langgraph/`
4. **Incorrect package listing**: `@liam-hq/github` was listed but doesn't exist in `frontend/packages/`

## Changes Made

- Reorganized Monorepo Structure into three clear sections:
  - Applications (apps)
  - Public Packages (publishable packages)
  - Internal Packages (internal-only packages)
- Added missing `@liam-hq/agent` package documentation
- Added `@liam-hq/db` and `@liam-hq/mcp-server` internal packages
- Added reference to LangGraph documentation for agent development
- Removed non-existent `@liam-hq/github` from the list (it's actually in `internal-packages`, not `packages`)

This improves accuracy and helps developers understand the codebase structure more clearly.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Expanded mo

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
