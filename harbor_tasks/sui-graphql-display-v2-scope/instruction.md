# Fix GraphQL Display v2 Scoping Issue

## Problem

The GraphQL API has a bug where Display v2 format objects fail to render for older versioned objects. The Display registry stores format templates as independent objects, but when rendering an object's display, the system incorrectly applies the object's own version constraint to the Display registry lookup. This causes valid Display v2 formats to be discarded when the rendered object has an older version than the display format.

## Symptoms

- Display v2 formats fail to render for objects with older versions
- The root version bound from the rendered object is incorrectly applied to the Display registry lookup
- Newer Display v2 formats cannot be found because the lookup is constrained by the rendered object's version

## File to Modify

- `crates/sui-indexer-alt-graphql/src/api/types/display.rs`

## Requirements

1. The code must compile after the fix: `cargo check -p sui-indexer-alt-graphql`
2. The fix must include a comment containing the exact phrase "Display registry objects are global objects" to explain why the version constraint should not apply to the Display registry lookup
3. Do NOT modify `crates/sui-indexer-alt-graphql/src/scope.rs`
4. The code must pass: `scripts/git-checks.sh`, `cargo xlint`, `cargo clippy -p sui-indexer-alt-graphql`

## Notes

- The `Scope` type controls version bounding for object lookups and is defined in `crates/sui-indexer-alt-graphql/src/scope.rs`
- Do NOT modify test files (`.move` and `.snap` files)
