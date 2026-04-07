# Backport MessageStorage NonEmptyArray Guards

## Problem

In `packages/cluster/src/MessageStorage.ts`, the `Encoded` type interface and the `makeEncoded` wrapper function accept plain `Array` and `ReadonlyArray` types for id list parameters (requestIds, shardIds, messageIds). This is unsafe because passing an empty array to methods like `repliesForUnfiltered` or `resetShards` will delegate to the underlying SQL storage with an empty `IN ()` clause, which produces invalid SQL or unexpected results.

The `makeEncoded` wrapper only partially guards against empty arrays — `repliesForUnfiltered` and `resetShards` have no guard at all and blindly delegate, while other methods use a simple `.length === 0` check instead of the type-safe `Arr.isNonEmptyArray` from the effect library.

## Expected Behavior

- The `Encoded` type should tighten all id list parameters to use `Arr.NonEmptyArray` instead of `Array` / `ReadonlyArray`
- The `makeEncoded` wrapper should guard every id list with `Arr.isNonEmptyArray`, short-circuiting to a safe default when the list is empty
- The SQL driver in `SqlMessageStorage.ts` should match the updated type signatures
- After fixing the code, update the project's agent instructions (`AGENTS.md`) to document the changeset requirement, and add an appropriate changeset file in `.changeset/` for the cluster package

## Files to Look At

- `packages/cluster/src/MessageStorage.ts` — the `Encoded` type and `makeEncoded` wrapper
- `packages/cluster/src/SqlMessageStorage.ts` — SQL driver with matching type signatures
- `AGENTS.md` — project agent instructions (should document the changeset policy)
- `.changeset/` — changeset files for versioning
