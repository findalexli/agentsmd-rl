# fix(ce-brainstorm): distinguish verification from technical design in Phase 1.1

Source: [EveryInc/compound-engineering-plugin#465](https://github.com/EveryInc/compound-engineering-plugin/pull/465)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-brainstorm/SKILL.md`

## What to add / change

Phase 1.1's "don't drift into technical planning" instruction conflated two activities: checking what currently exists (fact-checking) and deciding what to build (technical design). The blanket prohibition on inspecting "low-level architecture" prevented the skill from reading schema files, routes, or config — even when the brainstorm was about database tables. This caused unverified "table X does not exist" claims to be stated as fact and propagated into requirements documents.

The fix reframes the guardrail around the right distinction: defer *implementation decisions* (schemas, migration strategies, endpoint structure) to planning, but always permit *verification* of current state. Adds a rule that infrastructure existence claims must be verified against source files before being stated as fact — unverified claims must be labeled as assumptions.

Closes #457

---

[![Compound Engineering v2.59.0](https://img.shields.io/badge/Compound_Engineering-v2.59.0-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
🤖 Generated with Claude Opus 4.6 (1M context, extended thinking) via [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
