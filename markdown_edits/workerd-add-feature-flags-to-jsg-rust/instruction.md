# Add FeatureFlags support to JSG Rust bindings

## Problem

The Rust JSG bindings (`src/rust/jsg/`) currently have no way to access a worker's compatibility flags (feature flags). The `Realm` struct is created with just an isolate pointer, and `Lock` has no method to query which flags are enabled. This means Rust code that needs to branch on compatibility flags (e.g., `node_js_compat`, `fetch_refuses_unknown_protocols`) has to go through C++ FFI calls each time.

## Expected Behavior

Rust code should be able to query compatibility flags directly through the `Lock`:

```rust
if lock.feature_flags().get_node_js_compat() {
    // Node.js compatibility behavior
}
```

The flags should be parsed once from canonical Cap'n Proto bytes during `Realm` construction and cached — no re-parsing on each access.

## What needs to happen

1. **New module**: Create `src/rust/jsg/feature_flags.rs` with a `FeatureFlags` struct that wraps a capnp message reader for the `CompatibilityFlags` schema (`src/workerd/io/compatibility-date.capnp`). It should:
   - Accept canonical (single-segment, no segment table) Cap'n Proto bytes
   - Validate input (non-empty, word-aligned)
   - Provide a `reader()` method returning the capnp-generated `compatibility_flags::Reader`
   - Include unit tests

2. **Wire into Realm**: Update `src/rust/jsg/lib.rs` to:
   - Declare and export the `feature_flags` module
   - Add a `feature_flags: FeatureFlags` field to the `Realm` struct
   - Update `realm_create()` to accept `feature_flags_data: &[u8]` and construct `FeatureFlags`
   - Add `pub fn feature_flags()` method on `Lock` that returns the capnp reader

3. **C++ integration**: Update `src/workerd/io/worker.c++` to serialize the worker's `CompatibilityFlags` via `capnp::canonicalize()` and pass the bytes to `realm_create()`

4. **Test harness**: Update `src/rust/jsg-test/ffi.c++` to construct default (all-false) feature flags for the test realm

5. **Build files**: Add `capnp` and `compatibility-date_capnp_rust` dependencies to the relevant `BUILD.bazel` files

6. **Documentation**: After making the code changes, update the relevant documentation to reflect the new FeatureFlags API. The project's `src/rust/AGENTS.md` should be updated to cover this new capability in both the crate table and conventions section. The `src/rust/jsg/README.md` should also document the new feature, including the updated `realm_create` signature.

## Files to Look At

- `src/rust/jsg/lib.rs` — main JSG Rust module with Lock, Realm, and realm_create
- `src/rust/jsg/BUILD.bazel` — Bazel deps for jsg crate
- `src/workerd/io/worker.c++` — C++ side that creates the Rust Realm
- `src/rust/jsg-test/ffi.c++` — test harness FFI
- `src/rust/jsg-test/BUILD.bazel` — test harness deps
- `src/rust/AGENTS.md` — Rust crate documentation and conventions
- `src/rust/jsg/README.md` — JSG module documentation
- `src/workerd/io/compatibility-date.capnp` — CompatibilityFlags schema
