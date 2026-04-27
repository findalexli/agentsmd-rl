# feat(sentry-pack): build skill 9/30 — sentry-rate-limits

Source: [jeremylongshore/claude-code-plugins-plus-skills#399](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/399)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/saas-packs/sentry-pack/skills/sentry-rate-limits/SKILL.md`

## What to add / change

## Summary
- Rewrites `sentry-rate-limits` SKILL.md with production-grade Sentry rate limit management content
- Covers 9 steps: rate limit behavior & tiers, client-side sampling (`sampleRate`/`tracesSampleRate`/`tracesSampler`), `beforeSend` filtering, server-side inbound filters, per-key rate limits, spike protection, quota monitoring via Stats API v2, payload reduction, and fingerprinting
- Includes TypeScript and Python examples throughout, plus bash scripts for quota monitoring and bulk filter enablement
- Error handling table covers 8 failure scenarios with solutions

## Test plan
- [ ] `python3 scripts/validate-skills-schema.py --enterprise plugins/saas-packs/sentry-pack/` passes without errors for this skill
- [ ] SKILL.md body under 500-line limit (460 total, ~442 body)
- [ ] All required sections present: Overview, Prerequisites, Instructions (with Step headings), Output, Error Handling, Examples, Resources

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
