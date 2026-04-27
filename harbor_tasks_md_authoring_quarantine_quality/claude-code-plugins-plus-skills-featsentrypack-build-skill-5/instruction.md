# feat(sentry-pack): build skill 5/30 — sentry-error-capture

Source: [jeremylongshore/claude-code-plugins-plus-skills#396](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/396)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/saas-packs/sentry-pack/skills/sentry-error-capture/SKILL.md`

## What to add / change

## Summary
- Rewrote `sentry-error-capture` SKILL.md with production-quality `@sentry/node` v8 and `sentry-sdk` v2 patterns
- Dual-language coverage (TypeScript + Python) for captureException, captureMessage, withScope/push_scope, breadcrumbs, custom fingerprinting, and beforeSend filtering
- Enterprise validator score: **A (92/100)**

## Test plan
- [ ] `python3 scripts/validate-skills-schema.py --enterprise --verbose plugins/saas-packs/sentry-pack/skills/sentry-error-capture/SKILL.md` passes with A grade
- [ ] All code examples use real Sentry SDK imports (`@sentry/node`, `sentry_sdk`)
- [ ] No placeholder text or template artifacts remain

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
