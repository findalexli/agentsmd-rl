# Fix linked npm packages with peer deps failing to cache from lockfile

## Problem

When a workspace has linked npm packages that have peer dependencies, running Deno with a `deno.lock` file present produces a `Failed caching npm package` error. The error only occurs when:

1. A package is linked (via workspace links)
2. That linked package has peer dependencies
3. A `deno.lock` file exists

Without a lockfile, everything works fine. The issue is in how the lockfile snapshot resolution identifies which packages are linked (and thus shouldn't have dist/tarball info fetched).

## Expected Behavior

Linked packages should be correctly identified during lockfile snapshot resolution regardless of whether they have peer dependencies. The snapshot should assign `dist: None` for linked packages (since they're local) and `dist: Some(...)` for non-linked dependencies.

## Files to Look At

- `libs/npm/resolution/snapshot.rs` — contains the `snapshot_from_lockfile` function that builds the npm resolution snapshot from a lockfile. The link package identification logic is in this function.

## Hints

- Look at how link packages are collected and compared in `snapshot_from_lockfile`
- Consider what the serialized lockfile key looks like for packages with peer dependencies (e.g. `@myorg/shared@1.0.0_zod@4.3.6`) versus how link packages are represented
- The mismatch is between the format of the lookup key and the format of the comparison set
