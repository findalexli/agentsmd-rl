# feat(ce-plan): strengthen test scenario guidance across plan and work skills

Source: [EveryInc/compound-engineering-plugin#410](https://github.com/EveryInc/compound-engineering-plugin/pull/410)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/AGENTS.md`
- `plugins/compound-engineering/skills/ce-plan/SKILL.md`
- `plugins/compound-engineering/skills/ce-work-beta/SKILL.md`
- `plugins/compound-engineering/skills/ce-work/SKILL.md`

## What to add / change

## Summary

Users of `ce:work` are getting fewer tests than before. When `ce:plan` was rewritten from a code-heavy template to a "WHAT not HOW" decision artifact, the test guidance was compressed from rich, category-specific prompts (including a dedicated Integration Test Scenarios section) into a single vague line: "specific behaviors, edge cases, and failure paths to cover." Plans produced with thin test scenarios led `ce:work` to write thin tests.

## Approach

Restore category-driven test scenario guidance without reverting to pre-written code. The quality signal is specificity and proportionality to unit complexity — not a numeric target.

**ce:plan** — Plan Quality Bar, section 3.5 field definition, template, Phase 5.1 review checklist, and confidence check scoring now teach four test scenario categories (happy path, edge cases, error paths, integration) with explicit gating on when each applies. Template uses a single example line with an HTML comment instead of hardcoding all four categories, preventing mechanical padding.

**ce:work / ce:work-beta** — New "Test Scenario Completeness" table tells executors when each category applies and how to derive missing scenarios from the unit's own context. Subagent dispatch includes instruction to check category coverage.

## Extras

**AGENTS.md** — Adds stable/beta sync convention requiring explicit reasoning about whether to propagate changes between skill pairs.

---

[![Compound Engineering v2.54.1](https:

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
