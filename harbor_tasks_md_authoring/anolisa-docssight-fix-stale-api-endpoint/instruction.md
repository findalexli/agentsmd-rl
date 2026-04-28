# docs(sight): fix stale API endpoint table in AGENTS.md

Source: [alibaba/anolisa#397](https://github.com/alibaba/anolisa/pull/397)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `src/agentsight/AGENTS.md`

## What to add / change

## Summary

Fix stale API endpoint documentation in `AGENTS.md` that listed two endpoints removed during the `trace_id → conversation_id` naming migration (commit `c24f647`).

## Changes

- **Remove** stale endpoints that no longer exist:
  - `GET /api/interruptions/trace-counts`
  - `GET /api/traces/{id}/interruptions`

- **Add** their replacements introduced in the same migration:
  - `GET /api/interruptions/conversation-counts`
  - `GET /api/conversations/{id}/interruptions`

- **Add** missing endpoints not previously documented:
  - `GET /api/conversations/{id}` — conversation event detail
  - `GET /api/export/atif/conversation/{id}` — ATIF conversation export
  - `GET /api/token-savings` — token savings statistics

## Root Cause

The two trace-based endpoints (`/api/interruptions/trace-counts` and `/api/traces/{id}/interruptions`) were intentionally removed in `c24f647` as part of renaming `trace_id` to `conversation_id`. The documentation was not updated at the time, causing the endpoints to appear as available in `AGENTS.md` while returning 404 in practice.

## Related Issue

closes #388

## Type of Change

- [x] Documentation update

## Scope

- [x] `sight` (agentsight)

## Checklist

- [x] Code follows project conventions
- [x] Self-review completed

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
