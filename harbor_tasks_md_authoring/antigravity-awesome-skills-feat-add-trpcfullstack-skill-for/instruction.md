# feat: add trpc-fullstack skill for end-to-end type-safe API development

Source: [sickn33/antigravity-awesome-skills#329](https://github.com/sickn33/antigravity-awesome-skills/pull/329)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/trpc-fullstack/SKILL.md`

## What to add / change

# Pull Request Description

Adds a new `trpc-fullstack` skill covering end-to-end type-safe API development with tRPC. This fills a gap in the framework category — tRPC has 50M+ weekly npm downloads but had zero coverage in the repo.

The skill covers: routers & procedures, Zod input validation, context & middleware, auth-protected procedures, Next.js App Router adapter, server-side caller (for Server Components / SSR), React Query client setup, real-time subscriptions, and common pitfalls.

## Change Classification

- [x] Skill PR
- [ ] Docs PR
- [ ] Infra PR

## Issue Link (Optional)

N/A

## Quality Bar Checklist ✅

**All items must be checked before merging.**

- [x] **Standards**: I have read `docs/contributors/quality-bar.md` and `docs/contributors/security-guardrails.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `npm run validate`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag — set to `none` (pure TypeScript patterns, no shell commands, no network calls, no credential examples).
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Security**: Not applicable — this skill is `risk: none` and contains no offensive content.
- [x] **Safety scan**: Not applicable — this skill contains no shell commands, remote/network examples, or token-like strings. No `npm run security:docs` pass required.
- [ ] **Automated Skill Review**: Pending — will review and address any actionable feedba

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
