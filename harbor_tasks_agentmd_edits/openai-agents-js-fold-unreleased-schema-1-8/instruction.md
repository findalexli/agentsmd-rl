# Fold unreleased RunState schema changes into 1.8

## Problem

The `RunState` serialization schema in `packages/agents-core/src/runState.ts` was bumped to version `1.9` on `main` after the latest release tag (`v0.5.4`), but version `1.9` was never shipped in a release. The codebase now carries two unreleased schema versions (`1.8` for tool search items, `1.9` for batched computer actions and GA computer tool aliasing) that were both introduced after the last release. This creates a false compatibility boundary — any self-built snapshot from `main` between `1.8` and `1.9` would see a version mismatch, even though neither version was ever part of a released contract.

## Expected Behavior

Since both `1.8` and `1.9` are unreleased, their changes should be consolidated into a single schema version (`1.8`). The version history comment, the exported constant, the supported versions array, and any version-gated assertions should all reflect this consolidation. There should be no trace of `1.9` in the codebase.

Additionally, the repository's agent guidance documents should be updated to make this policy explicit: unreleased post-tag schema changes on `main` can be folded into the same next schema version rather than requiring a new version bump for each change. This applies to both the top-level `AGENTS.md` and the `.agents/skills/implementation-strategy/SKILL.md` — both currently imply that any persisted schema change requires a version bump, without distinguishing between released and unreleased formats.

## Files to Look At

- `packages/agents-core/src/runState.ts` — RunState serialization schema versioning
- `AGENTS.md` — contributor guide, section on Agents Core Runtime Guidelines and `$implementation-strategy`
- `.agents/skills/implementation-strategy/SKILL.md` — compatibility boundary rules for implementation decisions
