# Fix linked npm packages with peer deps failing to cache from lockfile

## Problem

When a workspace has linked npm packages that have peer dependencies, running Deno with a `deno.lock` file present produces a `Failed caching npm package` error. The error only occurs when:

1. A package is linked (via workspace links)
2. That linked package has peer dependencies
3. A `deno.lock` file exists

Without a lockfile, everything works fine.

## Expected Behavior

Linked packages should be correctly identified during lockfile snapshot resolution regardless of whether they have peer dependencies. The snapshot should assign `dist: None` for linked packages (since they're local) and `dist: Some(...)` for non-linked dependencies.

## File to Look At

- `libs/npm/resolution/snapshot.rs` — contains the `snapshot_from_lockfile` function that builds the npm resolution snapshot from a lockfile.

## Lockfile Key Format for Peer Dependencies

When a linked package has peer dependencies, its serialized lockfile key includes a peer-dep suffix. For example, `@myorg/shared@1.0.0` with a peer dependency on `zod@4.3.6` appears in the lockfile as `@myorg/shared@1.0.0_zod@4.3.6`. This is the **raw serialized key** stored in the lockfile.

## Symptom Description

The function iterates over lockfile entries using raw serialized keys. For linked packages with peer dependencies, the key includes a peer-dep suffix (e.g. `_zod@4.3.6`). During the lookup that determines whether a package is linked, this suffix causes linked packages with peer deps to not be recognized as linked — the resolver then incorrectly attempts to fetch their tarball, which fails for locally-linked packages. Linked packages without peer deps work correctly because their raw key has no suffix.

## Unit Test Requirement

You must add a unit test named `test_snapshot_from_lockfile_v5_with_linked_package_with_peer_deps` in `libs/npm/resolution/snapshot.rs` under the `mod tests` block. This test must:

- Define a lockfile with a workspace link to `@myorg/shared@1.0.0` and a peer dependency on `zod@4.3.6`
- The lockfile key for `@myorg/shared@1.0.0` in this case will be `@myorg/shared@1.0.0_zod@4.3.6`
- Assert that the linked package (`@myorg/shared`) has `dist: None` in the resulting snapshot
- Assert that the non-linked peer dep (`zod`) has `dist: Some(...)`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
