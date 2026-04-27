# fix(ce-work): make code review invocation mandatory by default

Source: [EveryInc/compound-engineering-plugin#453](https://github.com/EveryInc/compound-engineering-plugin/pull/453)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-work-beta/SKILL.md`
- `plugins/compound-engineering/skills/ce-work/SKILL.md`

## What to add / change

## Summary

The Code Review step in ce:work's Phase 3 lacked enforcement parity with other required steps (like "Prepare Operational Validation Plan (REQUIRED)"), making it easy for agents to rationalize skipping `ce:review`. An agent reported this as a bug in its own execution — it should have run ce:review automatically but didn't.

Three changes fix the incentive structure:

1. **Added `(REQUIRED)` tag** to the Code Review header, matching other mandatory steps
2. **Reordered tiers** — Tier 2 (full review) now appears first as the default action; Tier 1 is presented as the exception requiring explicit opt-out
3. **Requires explicit justification** before choosing Tier 1 — agents must state which criteria apply and why, rather than silently skipping review

Propagated to `ce-work-beta` (shared bug fix, not experimental behavior).

---

[![Compound Engineering v2.59.0](https://img.shields.io/badge/Compound_Engineering-v2.59.0-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
🤖 Generated with Claude Opus 4.6 (1M context, extended thinking) via [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
