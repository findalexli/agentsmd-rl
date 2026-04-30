# agents.md: minor fix

Source: [quran/quran.com-frontend-next#2499](https://github.com/quran/quran.com-frontend-next/pull/2499)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

- Documentation
  - Cleaned up agent-related documentation by removing an outdated automated snippet and associated metadata for clarity.
  - Simplified guidance by dropping an explicit lint/typecheck command from the instructions to avoid redundancy.
  - Streamlined build and deployment docs by removing a Vercel-specific bullet, keeping the section focused and current.
  - No functional changes to the product; updates are purely content edits to improve readability and reduce confusion.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
