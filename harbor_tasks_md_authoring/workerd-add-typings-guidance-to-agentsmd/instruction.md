# Add typings guidance to AGENTS.md based on review patterns

Source: [cloudflare/workerd#6548](https://github.com/cloudflare/workerd/pull/6548)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `types/AGENTS.md`

## What to add / change

## Summary

- Adds detailed guidance for adding/updating TypeScript types to `types/AGENTS.md`
- Adds three typings-specific anti-patterns to root `AGENTS.md`
- Cross-references `types/AGENTS.md` from the "Where to Look" table

## Motivation

Derived from reviewing ~15 recent PRs where typings feedback was given during code review. The recurring themes were:

1. **Generic ambient type names** (e.g., `Identity`, `Preview`, `Config`) causing potential collisions — flagged in #6413, #6375
2. **Bare `object` types** providing no value to users — flagged in #6413
3. **Index signatures** (`[key: string]: unknown`) added without justification — flagged in #6102
4. **Type changes made in wrong layer** (editing snapshots vs source) — flagged in #5575
5. **Unrelated formatting changes** mixed into type PRs — flagged in #5982
6. **Missing snapshot regeneration** after type source changes

The new guidance codifies these patterns so AI assistants (and human contributors) can get typings right on the first attempt rather than requiring review round-trips.

## Changes

### `types/AGENTS.md`
New "ADDING OR UPDATING TYPES" section covering:
- Where type changes belong (C++ RTTI vs `JSG_TS_OVERRIDE` vs `types/defines/`)
- Naming conventions for ambient types (product/feature prefix required)
- Interface design patterns (no bare `object`, index signature justification, JSDoc)
- Snapshot regeneration workflow
- Type test expectations
- PR hygiene

### `AGENTS.md` (root)
- Three new anti-pattern

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
