# feat(sentry-pack): build skill 3/30 — sentry-local-dev-loop

Source: [jeremylongshore/claude-code-plugins-plus-skills#394](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/394)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/saas-packs/sentry-pack/skills/sentry-local-dev-loop/SKILL.md`

## What to add / change

## Summary
- Rewrites `sentry-local-dev-loop` SKILL.md with production-quality content following the enterprise format (Frontmatter, Overview, Prerequisites, 3 Steps, Output, Error Handling, Examples, Resources, Next Steps)
- Step 1: Environment-aware `Sentry.init()` with DSN routing, debug mode, full sample rates, `beforeSend`/`beforeSendTransaction` console logging, and Spotlight integration
- Step 2: Verification script with `captureMessage`, `captureException`, `Sentry.startSpan()` for local perf profiling, breadcrumbs, and flush
- Step 3: Sentry Spotlight offline dev, `sentry-cli` source map upload/verify, and pre-push DSN leak hook
- Includes both TypeScript and Python examples with real SDK imports (`@sentry/node`, `sentry-sdk`)

## Test plan
- [ ] Validator passes enterprise tier (`python3 scripts/validate-skills-schema.py --enterprise --skills-only plugins/saas-packs/sentry-pack/`)
- [ ] All code examples use correct imports (`import * as Sentry from '@sentry/node'`, `import sentry_sdk`)
- [ ] No placeholder DSNs or fake package names
- [ ] URLs point to `sentry.io` not `sentry.com`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
