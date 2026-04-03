# Add `#[jsg_static_constant]` to Rust JSG

## Problem

The workerd Rust JSG bindings support exposing methods (`#[jsg_method]`), constructors, structs, and oneof types to JavaScript, but there is no way to expose numeric constants on a resource class. In C++ JSG, this is done with `JSG_STATIC_CONSTANT`, but no Rust equivalent exists.

Developers who need to define constants like `WebSocket.CONNECTING`, `WebSocket.OPEN`, etc. on a `#[jsg_resource]` type have no supported path — they would need to create static methods that return the value, which is incorrect (constants should be properties, not functions).

## Expected Behavior

A new `#[jsg_static_constant]` attribute macro should be available for `const` items inside `#[jsg_resource]` impl blocks. It should:

1. Expose the constant as a read-only numeric property on **both** the JavaScript constructor and prototype (matching Web IDL semantics)
2. Use the Rust constant name as-is for the JavaScript property name (no `snake_case` to `camelCase` conversion — constants are conventionally `UPPER_SNAKE_CASE` in both languages)
3. Support all standard numeric types (`i8`..`i64`, `u8`..`u64`, `f32`, `f64`)

## Files to Look At

- `src/rust/jsg-macros/lib.rs` — proc macro definitions; this is where the new attribute macro should be defined and where `generate_resource_impl` scans for attributes
- `src/rust/jsg/lib.rs` — runtime types (`Member` enum, resource descriptor construction); needs a new variant for constants
- `src/rust/jsg/v8.rs` — CXX FFI type definitions shared with C++; needs a descriptor struct for constants
- `src/rust/jsg/ffi.c++` — C++ side of the FFI bridge; needs to register constants on the V8 template

After implementing the feature, update the relevant project documentation to reflect the new macro. The `src/rust/AGENTS.md`, crate READMEs, and review checklist should all be kept in sync with what macros are available and how they work.
