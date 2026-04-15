# Fix linked npm packages with peer deps failing to cache from lockfile

## Problem

When a workspace has linked npm packages that have peer dependencies, running Deno with a `deno.lock` file present produces a `Failed caching npm package` error. The error only occurs when:

1. A package is linked (via workspace links)
2. That linked package has peer dependencies
3. A `deno.lock` file exists

Without a lockfile, everything works fine. The issue is in how the lockfile snapshot resolution identifies which packages are linked (and thus shouldn't have dist/tarball info fetched).

## Expected Behavior

Linked packages should be correctly identified during lockfile snapshot resolution regardless of whether they have peer dependencies. The snapshot should assign `dist: None` for linked packages (since they're local) and `dist: Some(...)` for non-linked dependencies.

## File to Look At

- `libs/npm/resolution/snapshot.rs` — contains the `snapshot_from_lockfile` function that builds the npm resolution snapshot from a lockfile. The link package identification logic is in this function.

## Lockfile Key Format for Peer Dependencies

When a linked package has peer dependencies, its serialized lockfile key includes a peer-dep suffix. For example, `@myorg/shared@1.0.0` with a peer dependency on `zod@4.3.6` appears in the lockfile as `@myorg/shared@1.0.0_zod@4.3.6`. This is the **raw serialized key** stored in the lockfile.

## What Must Be Fixed

The link-package lookup in `snapshot_from_lockfile` compares the raw serialized lockfile key (which includes peer-dep suffixes like `_zod@4.3.6`) against plain `name@version` strings. This format mismatch means linked packages with peer deps are never recognized as linked.

Correctly identify linked packages by comparing against the parsed `name` and `version` fields (`id.nv`) rather than the raw serialized key that includes peer-dep suffixes.

## Unit Test Requirement

You must add a unit test named `test_snapshot_from_lockfile_v5_with_linked_package_with_peer_deps` in `libs/npm/resolution/snapshot.rs` under the `mod tests` block. This test must:

- Define a lockfile with a workspace link to `@myorg/shared@1.0.0` and a peer dependency on `zod@4.3.6`
- The lockfile key for `@myorg/shared@1.0.0` in this case will be `@myorg/shared@1.0.0_zod@4.3.6`
- Assert that the linked package (`@myorg/shared`) has `dist: None` in the resulting snapshot
- Assert that the non-linked peer dep (`zod`) has `dist: Some(...)`

## Symptom Description

The bug manifests as a mismatch: the lookup key contains a peer-dep suffix (e.g. `@myorg/shared@1.0.0_zod@4.3.6`), but the link-package comparison set only stores plain `name@version` strings (e.g. `@myorg/shared@1.0.0`). Because the raw key never matches the comparison set, linked packages with peer deps are incorrectly treated as remote packages and the resolver attempts to fetch their tarball — which fails for locally-linked packages.