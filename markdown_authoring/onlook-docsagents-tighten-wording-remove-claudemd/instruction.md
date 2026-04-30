# docs(agents): tighten wording; remove CLAUDE.md

Source: [onlook-dev/onlook#2822](https://github.com/onlook-dev/onlook/pull/2822)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Description

Standardizes and tightens `AGENTS.md` based on current repo architecture and best‑practice guidance. Adds a crisp intro (“Actionable rules for repo agents—keep diffs minimal, safe, token‑efficient.”) and clarifies how agents should operate to produce small, correct diffs.

Highlights:
- Clear scope and repo map (App Router, API routers, editor service, shared packages).
- Next.js App Router guidance (default to Server Components; when to add `use client`; single client boundary for `observer` components).
- tRPC routing/export rules, Zod validation, and client usage patterns.
- Environment typing via `@t3-oss/env-nextjs`, `NEXT_PUBLIC_*` exposure, `env` import preference, and `next.config.ts` enforcement.
- Import boundaries and path aliases; avoid server‑only modules in client code (limited `path` exception), never import `process` in client.
- MobX store lifecycle patterns (`useState` construction, `useRef` retention, async cleanup, effect deps).
- Consolidated “Common Pitfalls” and “Context Discipline” for faster, safer agent changes.

Also removes `CLAUDE.md`, which was vendor‑specific. Guidance is now centralized and vendor‑agnostic in `AGENTS.md`, so Claude and all other agents share a single source of truth.

This helps:
- Reduce review overhead by promoting minimal, safe diffs.
- Prevent common runtime/build errors (env typing, client/server boundaries).
- Keep agent behavior consistent across tools and vendors.

## Related Issues

N/A

## Type of Chan

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
