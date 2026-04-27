# fix(onboarding): resolve section count contradiction with skip rule

Source: [EveryInc/compound-engineering-plugin#421](https://github.com/EveryInc/compound-engineering-plugin/pull/421)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/onboarding/SKILL.md`

## What to add / change

PR #413 added Section 2 ("How It's Used") with a skip rule for pure infrastructure repos, but left contradictory section-count language that could cause the agent to either produce an invalid 5-section doc or hallucinate a fake consumer view to satisfy the count.

Addresses [this review comment](https://github.com/EveryInc/compound-engineering-plugin/pull/413#discussion_r3003575978).

## Changes

- **Core principle 3**: Added explicit note that Section 2 may be skipped, producing five sections
- **Phase 2**: Fixed stale "five sections" → "six sections" (missed when PR #413 added Section 2)
- **Phase 3 intro**: Changed "exactly six sections" → "the sections defined below" (no longer hardcodes a count that conflicts with the skip rule)
- **Formatting requirements**: Changed "five sections" → "each section" (count-agnostic)

---

[![Compound Engineering v2.56.0](https://img.shields.io/badge/Compound_Engineering-v2.56.0-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
🤖 Generated with Claude Opus 4.6 (1M context, extended thinking) via [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
