# Add FeatureFlags Support to JSG Rust Bindings

## Problem

Rust code in the `jsg` crate currently has no way to access workerd's compatibility flags (defined in `src/workerd/io/compatibility-date.capnp`). When implementing Rust-side APIs that need to behave differently based on compatibility flags (e.g., `nodejs_compat`, `url_standard`), there's no mechanism to query these flags from within the Rust JSG layer.

The `Realm` (created via `realm_create()`) is initialized without any knowledge of the worker's feature flags, and `Lock` has no method to expose them to Rust API code.

## Expected Behavior

1. A new `FeatureFlags` type in the `jsg` crate should wrap the worker's compatibility flags, parsed from Cap'n Proto canonical bytes.
2. `realm_create()` should accept the serialized compatibility flags from C++ and store them in the `Realm`.
3. `Lock` should expose a `feature_flags()` method returning a capnp reader so Rust code can query individual flags like `get_node_js_compat()`.
4. The C++ call site in `src/workerd/io/worker.c++` must canonicalize the feature flags and pass them through FFI.
5. Build files and the test harness must be updated to support the new dependency on the compatibility-date capnp schema.

After implementing the code changes, update the relevant documentation and agent instruction files to reflect the new FeatureFlags capability. The project's `src/rust/AGENTS.md` and `src/rust/jsg/README.md` should be updated to document this new feature.

## Files to Look At

- `src/rust/jsg/lib.rs` — Main JSG Rust crate: `Lock`, `Realm`, `realm_create()`, CXX bridge
- `src/rust/jsg/BUILD.bazel` — Bazel deps for the jsg Rust crate
- `src/workerd/io/worker.c++` — C++ side that initializes the Rust realm
- `src/rust/jsg-test/ffi.c++` — Test harness C++ that calls `realm_create()`
- `src/rust/jsg-test/BUILD.bazel` — Test harness build deps
- `src/workerd/io/compatibility-date.capnp` — Cap'n Proto schema for compatibility flags
- `src/rust/AGENTS.md` — Agent instructions for the Rust crates
- `src/rust/jsg/README.md` — JSG crate documentation
