# Task: Clean Up Dead Code in Indexer Framework

## Problem

The `sui-indexer-alt-framework-store-traits` crate contains dead code that triggers warnings during compilation and static analysis. A recent refactoring removed the `sequential_connect` method and the `anyhow::Context` import that were only used by it, leaving them unused. This vestigial code should be removed to keep the codebase clean.

## Your Task

1. Navigate to the `sui-indexer-alt-framework-store-traits` crate source code
2. Remove the unused `sequential_connect` method from the `SequentialStore` trait
3. Remove the unused `anyhow::Context` import
4. Ensure the crate remains fully functional after cleanup

## Verification

Your changes should:
- Result in code that compiles cleanly (`cargo check -p sui-indexer-alt-framework-store-traits`)
- Pass clippy without warnings (`cargo clippy -p sui-indexer-alt-framework-store-traits -- -D warnings`)
- Pass all existing unit tests (`cargo test --lib -p sui-indexer-alt-framework-store-traits`)
- Be properly formatted (`cargo fmt -p sui-indexer-alt-framework-store-traits`)

## Constraints

- The `SequentialStore` trait must continue to exist
- The `transaction` method within `SequentialStore` must be preserved
- Do not change any public APIs that might break downstream consumers
