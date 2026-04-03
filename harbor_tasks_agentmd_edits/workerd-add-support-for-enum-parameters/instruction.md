# Add `#[jsg_oneof]` macro for enum union parameters in Rust JSG

## Problem

The Rust JSG (JavaScript Glue) bindings in `src/rust/jsg-macros/` currently support `#[jsg_struct]`, `#[jsg_method]`, and `#[jsg_resource]` proc macros. However, there's no way to define a union/variant type that can accept one of several JavaScript types as a method parameter — the Rust equivalent of C++ JSG's `kj::OneOf<>`.

For example, a method that should accept either a string or a number currently cannot express this in the type system.

## Expected Behavior

1. A new `#[jsg_oneof]` proc macro attribute should be available for enums, generating `jsg::Type` and `jsg::FromJS` implementations. Each enum variant should be a single-field tuple variant wrapping a type that already implements the JSG traits.

2. The generated code should try each variant's type in declaration order without coercion — if a JavaScript string is passed to a `StringOrNumber` enum, it should match the `String` variant directly. If no variant matches, a `TypeError` should be thrown listing all expected types.

3. The `FromJS` trait in `src/rust/jsg/wrappable.rs` needs a `try_from_js_exact` method that attempts conversion only when the JavaScript type matches exactly (returning `None` if it doesn't). This is used by the macro to try each variant.

4. Reference parameters (`&EnumType`) should also work, requiring a blanket `FromJS` impl for `&T`.

## Files to Look At

- `src/rust/jsg-macros/lib.rs` — existing proc macros live here; add the new one
- `src/rust/jsg/wrappable.rs` — the `FromJS` trait definition
- `src/rust/jsg-test/tests/` — test module registration

After implementing the code changes, update the relevant documentation (READMEs) to describe the new macro, its usage, and its relationship to C++ JSG's union types.
