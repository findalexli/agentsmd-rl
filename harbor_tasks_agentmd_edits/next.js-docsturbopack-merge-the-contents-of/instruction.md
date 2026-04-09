# Merge the cells page documentation into rustdocs

## Problem

The Turbopack project has been maintaining documentation about cells and `Vc` (Value Cells) in two places:
1. An external mdbook at https://turbopack-rust-docs.vercel.sh/turbo-engine/cells.html
2. Inline rustdoc comments in the `turbo-tasks` crate

This split creates a maintenance burden and can lead to outdated or inconsistent documentation. The external mdbook has more detailed explanations that should be merged into the official rustdocs.

## Expected Behavior

Merge the content from the cells page in the external mdbook into the `turbo-tasks` crate rustdocs. Specifically:

1. Create a new `README.md` file in `turbopack/crates/turbo-tasks/src/vc/` containing the merged cells documentation
2. Update `mod.rs` to use `#[doc = include_str!("README.md")]` to embed the README as the module documentation
3. Remove the old inline documentation from `mod.rs` (it will be replaced by the README include)
4. Update `lib.rs` documentation to improve wording about what a `Vc` represents
5. Update `raw_vc.rs` with improved documentation links
6. Update `resolved.rs` with a new "Reading a ResolvedVc" section
7. Update the crate `README.md` to merge the Cells bullet point into the Vc description
8. Fix a typo in `mod.rs` (missing backtick in code example)
9. Update `.alexrc` to allow the word "dirty" (needed for cell update documentation)

## Files to Look At

- `turbopack/crates/turbo-tasks/src/vc/mod.rs` — Main Vc module, needs to use `include_str!` for docs
- `turbopack/crates/turbo-tasks/src/vc/README.md` — New file to create with merged cells documentation
- `turbopack/crates/turbo-tasks/README.md` — Top-level crate README, needs Cells/Vc section merged
- `turbopack/crates/turbo-tasks/src/lib.rs` — Entry point, Vc macro documentation needs updates
- `turbopack/crates/turbo-tasks/src/raw_vc.rs` — RawVc type documentation needs Vc links
- `turbopack/crates/turbo-tasks/src/vc/resolved.rs` — Needs new "Reading a ResolvedVc" section
- `.alexrc` — Add "dirty" to allowed words list

## Key Documentation Content to Include

The new `README.md` should cover:
- What value cells are (computation results, like spreadsheet cells)
- How to construct a cell using `.cell()` or `Vc::cell`
- How cell updates work (invalidation, re-execution)
- Reading Vcs with `.await` and `ReadRef`
- Subtypes: `ResolvedVc` and `OperationVc`
- The comparison table showing differences between Vc types
- Eventual consistency behavior
- Local outputs optimization
