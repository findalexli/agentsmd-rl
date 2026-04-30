# Add internal header security guideline to AGENTS.md

Source: [vercel/next.js#92128](https://github.com/vercel/next.js/pull/92128)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

Adds a security guideline to `AGENTS.md` that instructs the PR reviewer to flag new code that reads non-standard request headers without checking them against the `INTERNAL_HEADERS` filter list in `packages/next/src/server/lib/server-ipc/utils.ts`.

## Context

`filterInternalHeaders()` strips internal headers from incoming requests at the router-server entry point. When new internal headers are introduced but not added to the filter list, external attackers can forge them. This guideline helps catch those gaps during code review.

Validated in #92122 — the reviewer successfully flagged a test violation using this guideline.

## Test plan

- [x] Verified the reviewer catches unfiltered header reads with this guideline (see #92122)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
