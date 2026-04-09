# Fix GraphQL Display v2 Scoping Issue

## Problem

The GraphQL API has a bug where it incorrectly bounds the version lookup for Display v2 format objects. When rendering an object's display, the system was applying the object's own version constraint to the Display registry lookup. This caused valid Display v2 formats to be discarded when querying older objects.

## Symptoms

- Display v2 formats fail to render for older objects
- The `display_v2` function in the GraphQL API is not correctly resolving display registry objects
- Newer Display v2 objects cannot be found when the root version bound is applied from the value being rendered

## Files to Modify

Primary file:
- `crates/sui-indexer-alt-graphql/src/api/types/display.rs`

Related files for understanding:
- `crates/sui-indexer-alt-graphql/src/scope.rs` - defines the `Scope` type and `without_root_bound()` method

## Key Context

The Display registry stores format templates as global objects, not as children of the objects being rendered. When the GraphQL API looks up a Display v2 format for an object, it was incorrectly inheriting the root version bound from the object itself. This prevented newer display formats from being found for older objects.

The `Scope` type has a method `without_root_bound()` that creates a new scope without the root version bound, intended for exactly this use case - when looking up global objects that should not be constrained by the version of some related object.

## What the Fix Should Do

In the `display_v2` function, before calling `Object::latest()` to fetch the display registry object, the scope should be modified to remove the root version bound. This allows the display registry lookup to find the latest version regardless of the object's version.

## Testing

After applying the fix:
1. Code should compile: `cargo check -p sui-indexer-alt-graphql`
2. The fix should include an explanatory comment about why the root bound is being removed
3. Run the repo's standard checks: `cargo xclippy`, `cargo fmt`

## Notes

- Do NOT modify the test files (`.move` and `.snap` files) - those are for the full e2e test suite which requires database setup
- Focus only on the fix in `display.rs`
- The fix is a 5-line addition including comments
