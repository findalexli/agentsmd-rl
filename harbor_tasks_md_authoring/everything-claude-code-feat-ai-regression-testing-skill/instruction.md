# feat: AI Regression Testing skill

Source: [affaan-m/everything-claude-code#433](https://github.com/affaan-m/everything-claude-code/pull/433)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/ai-regression-testing/SKILL.md`

## What to add / change

## Summary
Adds a new skill ai-regression-testing focused on catching regressions introduced by AI coding agents. Covers sandbox/production parity testing, API response shape verification, and bug-check workflow integration. Based on real-world experience where Claude Code introduced the same bug 4 times - only automated tests caught it.

## Key Patterns
- Sandbox/Production Mismatch: AI fixes one code path but forgets the other
- SELECT Clause Omission: New DB column added to response but not to query
- Error State Leakage: Adding error handling without clearing stale data
- Optimistic Update Rollback: Missing rollback on API failure

## Why This Matters
When the same AI model writes code and reviews it, it carries the same blind spots into both steps. This skill provides patterns to break that cycle using automated tests.

Generated with Claude Code

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Adds the `ai-regression-testing` skill with practical patterns and helpers to catch regressions common in AI-assisted code changes. Focuses on sandbox/production parity, API response contracts, and a bug-check workflow that runs tests before reviews.

- **New Features**
  - Adds `skills/ai-regression-testing/SKILL.md` with setup for `vitest` + `Next.js` App Router (sandbox mode, `vitest.config.ts`, `__tests__/setup.ts`).
  - Provides test helpers for Next.js route handlers and JSON parsing.
  - Includes example tests for sandbox/production parity a

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
