# Unnecessary Heap Allocations in NAPI Object Structs

## Problem

Several `#[napi(object)]` structs in `crates/next-napi-bindings/src/next_api/` are declared with `String` fields, even though the source data they're constructed from is `RcStr` (a reference-counted string type from the `turbo-rcstr` crate). This means every time one of these structs is created, the code performs a needless heap allocation — converting the `RcStr` to an owned `String` via `.to_string()` or `.into_owned()` — only to immediately hand it to the NAPI serializer.

This is wasteful because `RcStr` already implements `ToNapiValue` and `FromNapiValue` (behind the `napi` feature flag in `turbo-rcstr`, which is already enabled in the `next-napi-bindings` crate). Using `RcStr` directly would avoid the allocation entirely — just an atomic refcount increment on clone.

## Affected Files

- `crates/next-napi-bindings/src/next_api/endpoint.rs` — `NapiAssetPath` struct
- `crates/next-napi-bindings/src/next_api/project.rs` — `NapiRoute` struct and `from_route` method
- `crates/next-napi-bindings/src/next_api/utils.rs` — `NapiIssue`, `NapiAdditionalIssueSource`, `NapiSource`, `NapiDiagnostic` structs

## Expected Behavior

The struct field types should use `RcStr` instead of `String` where the source data is already `RcStr`, and the corresponding `From` / constructor impls should use `.clone()` or direct field moves rather than allocating conversions. The JavaScript API surface is unchanged since both `String` and `RcStr` serialize to a JS `string` via the same underlying `napi_create_string_utf8` call.

## Hints

- Check what types the `From<...>` impls convert from — if the source field is `RcStr`, the struct field should match.
- The `turbo_rcstr::RcStr` import may need to be added in files that don't already have it.
- Make sure function signatures that construct these structs also accept `RcStr` where they previously took `String`.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`
