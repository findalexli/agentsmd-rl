# feat(ce-work): accept bare prompts and add test discovery

Source: [EveryInc/compound-engineering-plugin#423](https://github.com/EveryInc/compound-engineering-plugin/pull/423)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-work-beta/SKILL.md`
- `plugins/compound-engineering/skills/ce-work/SKILL.md`

## What to add / change

## Summary

ce:work now handles bare prompts (not just plan files) and includes test discovery as a first-class execution step.

**Phase 0 — Input Triage** routes bare prompts through a complexity assessment before execution. Trivial work skips ceremony entirely, small/medium work gets an inline task list, and large work surfaces a recommendation toward brainstorm/plan without forcing it. When a plan document is provided, Phase 0 is skipped entirely — no overhead for the existing pipeline.

**Test Discovery** is a new universal step in the Phase 2 execution loop. Before changing a file, the agent finds its existing test files (by import, naming pattern, or shared references). When a plan specifies test scenarios, the agent starts there and supplements with any coverage the plan missed. Test guidance throughout the skill now uses "add/update/remove" instead of just "add new tests."

Both changes propagated to ce:work-beta — they're orthogonal to the delegate mode that beta exists to test.

---

[![Compound Engineering v2.54.1](https://img.shields.io/badge/Compound_Engineering-v2.54.1-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
🤖 Generated with Claude Opus 4.6 (1M context) via [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
