# Task: Remove unused SequentialStore::sequential_connect function

## Problem Description

The `SequentialStore` trait in the `sui-indexer-alt-framework-store-traits` crate contains a vestigial method `sequential_connect` that is no longer used anywhere in the codebase. This method was introduced during a recent refactoring but has since become dead code.

Additionally, the `anyhow::Context` import at the top of the file is only used by this unused method and should also be removed.

## Files to Modify

- `crates/sui-indexer-alt-framework-store-traits/src/lib.rs`

## What Needs to be Done

1. Remove the `sequential_connect` method from the `SequentialStore` trait
2. Remove the unused `use anyhow::Context;` import

## Verification

After making the changes:
- The crate should compile successfully with `cargo check -p sui-indexer-alt-framework-store-traits`
- The broader indexer crates (`sui-indexer-alt-framework`, `sui-indexer-alt`) should still compile

## Hints

- Look for the `SequentialStore` trait definition in the file
- The method to remove is an async function that calls `self.connect()` and adds an error context
- Make sure to remove the import only if `Context` is not used elsewhere in the file
