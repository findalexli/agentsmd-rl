# Consolidate turbo-tasks crate documentation into README.md

## Problem

The `turbo-tasks` crate (`turbopack/crates/turbo-tasks/`) has its crate-level documentation written as inline `//!` doc comments at the top of `src/lib.rs`. This documentation is limited in scope — it covers the basic primitives but lacks detail on the task graph, incremental builds, and how functions and tasks work together.

Additionally, the crate has no `README.md`, which means developers browsing the directory or viewing it on GitHub have no quick reference for what this crate does and how it works.

## Expected Behavior

The crate-level documentation should be moved from inline `//!` comments in `lib.rs` to a `README.md` file at the crate root (`turbopack/crates/turbo-tasks/README.md`). The `lib.rs` file should use Rust's `#![doc = include_str!(...)]` pattern to pull in the README as crate documentation, so it still appears in `cargo doc` output.

The README should expand on the existing docs to cover:
- The 4 turbo-tasks primitives (Functions, Values, Traits, Collectibles) and derived elements (Tasks, Cells, Vcs)
- How functions and tasks work (memoization, dependency tracking, parallel execution)
- The task graph and invalidation propagation
- The incremental rebuild mechanism

## Files to Look At

- `turbopack/crates/turbo-tasks/src/lib.rs` — currently holds the inline crate docs that need to be moved
- `turbopack/crates/turbo-tasks/README.md` — does not exist yet; needs to be created with the expanded documentation
