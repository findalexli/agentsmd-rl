# feat(sentry-pack): build skill 18/30 — sentry-reference-architecture

Source: [jeremylongshore/claude-code-plugins-plus-skills#407](https://github.com/jeremylongshore/claude-code-plugins-plus-skills/pull/407)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/saas-packs/sentry-pack/skills/sentry-reference-architecture/SKILL.md`

## What to add / change

## Summary
- Rewrote `sentry-reference-architecture` SKILL.md with real Sentry architecture patterns
- Centralized config module (`lib/sentry.ts`) with PII scrubbing, environment-aware sample rates, health check exclusion via `tracesSampler`
- Project structure strategy: one-project-per-service vs shared project with decision criteria table
- Error handling middleware for Express, FastAPI, and Django with severity-based capture
- Distributed tracing: automatic HTTP (SDK v8) + manual propagation helpers for message queues and gRPC
- Team-based alert routing with ownership rules and 4-tier escalation (P0-P3)
- Source map uploads: CLI script + Webpack plugin for monorepo/Turborepo builds
- `SentryService` singleton wrapper with idempotent init, custom metrics, and graceful shutdown
- 394 lines (under 500-line limit), all enterprise sections present (Overview, Prerequisites, Instructions, Output, Error Handling, Examples, Resources, Next Steps)

## Test plan
- [x] Enterprise validator passes (no errors for this skill, avg score 86.3 → 86.8)
- [x] Scoped `Bash(npm:*), Bash(npx:*)` — no unscoped Bash error
- [x] All 8 required sections present
- [x] Under 500-line body limit (394 lines)
- [ ] CI validation passes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
