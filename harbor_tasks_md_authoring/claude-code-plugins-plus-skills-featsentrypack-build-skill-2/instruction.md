# feat(sentry-pack): build skill 21/30 — sentry-incident-runbook

Source: [jeremylongshore/claude-code-plugins-plus-skills#411](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/411)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/saas-packs/sentry-pack/skills/sentry-incident-runbook/SKILL.md`

## What to add / change

## Summary
- Enterprise-tier rewrite of `sentry-incident-runbook` SKILL.md with full incident response lifecycle
- P0-P3 severity classification with decision tree, 11-point triage checklist, Sentry Discover queries (`count()`, `count_unique(user)`, `p95(transaction.duration)`), API-driven resolution with regression detection, stakeholder communication templates, and postmortem template with Sentry data exports
- Three concrete incident examples covering P0 payment failure, P2 upstream API, and P1 deployment regression
- Pack average score: 86.6 → 87.0 (this skill eliminated both `## Overview` and `## Examples` enterprise errors)

## Test plan
- [ ] `python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/saas-packs/sentry-pack/` passes with 0 errors for this skill
- [ ] Verify 29 missing `## Overview` errors (not 30) confirming this skill has the section
- [ ] All bash code blocks include error handling (`|| echo "ERROR: ..."`)
- [ ] No placeholder text (`{custom}`, `{person}`, etc.)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
