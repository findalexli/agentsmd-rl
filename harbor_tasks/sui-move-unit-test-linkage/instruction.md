# Fix Move Unit Test Runner Linkage Context

## Problem

The Move unit test runner fails to properly provide full linkage for packages during test setup, causing compilation or linking errors when running tests that involve cross-package dependencies.

The bug manifests as build failures or linker errors when a test in one package depends on modules from another package with a different address. The test runner's package storage setup doesn't properly initialize linkage context for cross-module references.

## Verification

After the fix:
1. `cargo check -p move-unit-test` must pass without errors
2. `cargo build -p move-unit-test --lib` must complete successfully
3. Cross-package tests must run without linkage errors

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`
