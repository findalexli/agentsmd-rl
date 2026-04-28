# chore: simplify CLAUDE.md documentation

Source: [liam-hq/liam#3505](https://github.com/liam-hq/liam/pull/3505)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Issue

- resolve: Simplify CLAUDE.md for better maintainability and clarity

## Why is this change needed?

The CLAUDE.md file had become verbose and contained redundant information that made it harder to navigate and maintain. This change streamlines the documentation to focus on essential information while maintaining all critical development guidelines.

## Summary

- Removed verbose project overview and detailed command examples
- Consolidated essential commands into concise bullet points  
- Removed redundant sections and important files list
- Maintained core development guidelines and architecture information
- Applied the "less is more" principle throughout the document

## Test plan

- [x] Verified all essential commands and guidelines are preserved
- [x] Ensured no critical information was lost during simplification
- [x] Confirmed the document structure remains logical and easy to navigate

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
