# Unnecessary public visibility in ty display types

## Problem

The file `crates/ty_python_semantic/src/types/display.rs` in the ty type checker contains a number of items (structs, enums, methods, and fields) with `pub` or `pub(crate)` visibility that is broader than necessary. These items are only used within the `types` module and should have module-private visibility instead.

Additionally, some methods appear to be dead code — they are not called anywhere in the codebase.

## Expected Behavior

All items in `display.rs` that are only used internally should have their visibility reduced to the minimum required (module-private where appropriate). Dead code methods should be removed entirely. The crate must still compile successfully after these changes.

## Files to Look At

- `crates/ty_python_semantic/src/types/display.rs` — contains the display types with overly broad visibility modifiers
