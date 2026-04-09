# Merge mdbook cells documentation into rustdocs

## Task

Merge the contents of the external "cells" documentation page from the Turbopack mdbook into the inline Rust documentation (rustdocs) for the `turbo-tasks` crate.

## What needs to be done

1. **Create new Vc README.md**: Create `turbopack/crates/turbo-tasks/src/vc/README.md` with comprehensive documentation about Value Cells (`Vc`). This should cover:
   - What value cells are and how they work
   - Understanding cells (immutability, recomputability, dependency tracking, persistence)
   - Constructing and updating cells
   - Reading `Vc`s
   - Subtypes (`ResolvedVc`, `OperationVc`)
   - Equality, hashing, execution model, eventual consistency
   - Optimization: Local Outputs

2. **Refactor mod.rs to use include_str!**: Replace the large inline doc comment in `turbopack/crates/turbo-tasks/src/vc/mod.rs` with `#[doc = include_str!("README.md")]` to embed the new README.

3. **Update crate-level README.md**: Consolidate the separate "Cells" and "Vc" entries in `turbopack/crates/turbo-tasks/README.md` into a single, clearer description.

4. **Fix documentation typos and inaccuracies**:
   - In `src/lib.rs`: Update the `value` macro documentation to reference `bincode::Encode`/`bincode::Decode` instead of `serde::Serialize`/`serde::Deserialize`
   - In `src/lib.rs`: Update the `Vc` description text
   - In `src/raw_vc.rs`: Fix intra-doc links for `Vc` references
   - In `src/vc/mod.rs`: Fix typo in `upcast_non_strict` docs (double space after period)
   - In `src/vc/resolved.rs`: Add a new "Reading a ResolvedVc" section

5. **Update .alexrc**: Add "dirty" to the word denylist

## Key files to modify

- `turbopack/crates/turbopack/crates/turbo-tasks/src/vc/README.md` — CREATE this file
- `turbopack/crates/turbo-tasks/src/vc/mod.rs` — use `include_str!`, fix typo
- `turbopack/crates/turbo-tasks/README.md` — consolidate cells/vc description
- `turbopack/crates/turbo-tasks/src/lib.rs` — update macro docs (bincode, Vc description)
- `turbopack/crates/turbo-tasks/src/raw_vc.rs` — fix doc links
- `turbopack/crates/turbo-tasks/src/vc/resolved.rs` — add reading section
- `.alexrc` — add "dirty" to denylist

## Expected outcome

After your changes:
- `cargo check` should pass in `turbopack/crates/turbo-tasks`
- The new `README.md` should exist with substantial documentation
- The inline docs in `mod.rs` should be replaced with `include_str!`
- All documentation should be accurate and consistent with the turbo-tasks architecture

## Context

The Turbopack project maintains documentation in both an mdbook (separate documentation site) and rustdoc (inline API docs). This PR consolidates the "cells" documentation from the external mdbook into the crate's rustdocs for better discoverability and maintenance.
