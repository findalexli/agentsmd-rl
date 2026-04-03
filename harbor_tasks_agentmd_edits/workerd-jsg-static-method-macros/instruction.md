# Add Static Method Support to Rust JSG Macros

## Problem

The `#[jsg_method]` proc macro in `src/rust/jsg-macros/lib.rs` currently assumes every annotated method is an instance method — it always unwraps `&self` from the V8 `this` argument and calls `self_.method_name(args)`. This means there is no way to define static methods on a JSG resource class (methods callable on the constructor itself, like `MyClass.create()`, rather than on instances).

Similarly, the `#[jsg_resource]` macro on impl blocks always emits `jsg::Member::Method` for every `#[jsg_method]`, placing them all on the prototype. There is no `jsg::Member::StaticMethod` variant being generated.

## Expected Behavior

Methods annotated with `#[jsg_method]` that **do not** have a receiver (`&self` or `&mut self`) as their first parameter should be automatically detected as static methods:

1. **In the callback**: the generated FFI callback should call `Self::method_name(args)` directly instead of unwrapping a `self` reference from `this`.
2. **In the resource impl**: the method should be registered as a `StaticMethod` member (on the constructor) rather than a `Method` member (on the prototype).
3. **FFI support**: you'll need to add a C++ FFI function that can materialize a V8 `Function` from a `FunctionTemplate` (using V8's `GetFunction` API), and expose it through the Rust FFI bridge. A new `Function` type in `v8.rs` with the appropriate conversion traits is also needed.

Instance methods (with `&self`/`&mut self`) must continue to work exactly as before.

After implementing the code changes, update the relevant project documentation to reflect the new static method behavior:
- The conventions in `src/rust/AGENTS.md` should describe how receiver presence determines method type
- The macro documentation in `src/rust/jsg-macros/README.md` should explain and show examples of both instance and static methods
- The review checklist in `docs/reference/rust-review-checklist.md` should note the receiver-based distinction

## Files to Look At

- `src/rust/jsg-macros/lib.rs` — the proc macro implementations for `jsg_method` and `jsg_resource`
- `src/rust/jsg/v8.rs` — V8 type wrappers and FFI declarations
- `src/rust/jsg/ffi.c++` / `src/rust/jsg/ffi.h` — C++ FFI bridge functions
- `src/rust/AGENTS.md` — Rust crate conventions
- `src/rust/jsg-macros/README.md` — macro usage documentation
- `docs/reference/rust-review-checklist.md` — Rust code review checklist
