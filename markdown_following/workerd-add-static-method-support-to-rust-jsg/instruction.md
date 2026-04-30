# Add static method support to Rust JSG bindings

## Problem

The `#[jsg_method]` proc macro in `src/rust/jsg-macros/lib.rs` currently assumes every method annotated with it is an instance method. It always generates code that unwraps `self` from the V8 callback arguments (`args.this()` + `unwrap_resource`). This means there is no way to define static methods on JSG resource types — methods that should be called on the class constructor (e.g., `MyClass.create(...)`) rather than on instances.

When a Rust function without `&self` or `&mut self` is annotated with `#[jsg_method]`, the generated callback will crash at runtime because it tries to unwrap a `self` reference from a call that has no `this` binding.

## Expected Behavior

The `#[jsg_method]` macro should automatically detect whether a method has a receiver (`&self` / `&mut self`):

- **Instance methods** (with receiver): registered on the prototype, called on object instances — current behavior, should be preserved.
- **Static methods** (without receiver): registered on the constructor, called on the class itself — new behavior.

This requires changes across several layers:

1. The proc macro (`jsg-macros/lib.rs`) must use the `syn` crate's `FnArg::Receiver` variant to detect the presence of a receiver (`&self` / `&mut self`) and branch accordingly:
   - In `jsg_method`: generate different invocation code for instance vs static methods (instance methods unwrap `self` via `args.this()`, static methods call via `Self::method_name(...)`)
   - In `generate_resource_impl`: emit different `Member::` enum variants for each case (the `jsg` crate already defines the necessary variant types)
2. The V8 FFI layer (`jsg/ffi.h`, `jsg/ffi.c++`, `jsg/v8.rs`) must support extracting the constructor `Function` from a `FunctionTemplate` using V8's `GetFunction` API, so static methods can be exposed on it. This involves:
   - Defining a `Function` struct type in `v8.rs` (analogous to the existing `Object` and `FunctionTemplate` structs)
   - Declaring and implementing the FFI bridge function in `ffi.h` and `ffi.c++`
   - Adding a `From<Local<'_, Function>>` to `Local<'_, Value>` conversion in `v8.rs`
   - Adding a method on `Global<FunctionTemplate>` to retrieve the local `Function`

After implementing the code changes, update the relevant documentation to reflect the new static method support. The project's `src/rust/AGENTS.md`, `src/rust/jsg-macros/README.md`, and `docs/reference/rust-review-checklist.md` should all be updated to document this new behavior.

## Files to Look At

- `src/rust/jsg-macros/lib.rs` — the proc macro implementation (`jsg_method` and `generate_resource_impl`)
- `src/rust/jsg/v8.rs` — V8 type bindings and FFI declarations
- `src/rust/jsg/ffi.h` — C++ FFI header
- `src/rust/jsg/ffi.c++` — C++ FFI implementation
- `src/rust/AGENTS.md` — conventions for JSG resource types
- `src/rust/jsg-macros/README.md` — documentation for the proc macros
- `docs/reference/rust-review-checklist.md` — Rust review checklist covering JSG patterns

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo fmt (Rust formatter)` — the project's Rust formatting configuration lives in `src/rust/rustfmt.toml` (which defines `group_imports` and `imports_granularity` settings)
