# Task: Re-export ReadLevel for Rust Client

## Problem

The `ReadLevel` type from `chroma_types::plan` is not currently re-exported in the `chroma` crate's public API. This means users need to depend on the internal `chroma_types` crate directly to access this type, which is undesirable for a public client API.

## Goal

Make `ReadLevel` available through the `chroma` crate's public API by re-exporting it from the `types` module.

## Files to Modify

1. **`rust/chroma/src/types.rs`** - Add a re-export for `ReadLevel` from `chroma_types::plan`
2. **`rust/chroma/src/collection.rs`** - Update the doc examples to use the new re-export path (`chroma::types::ReadLevel` instead of `chroma_types::plan::ReadLevel`)

## Requirements

- `ReadLevel` must be accessible via `chroma::types::ReadLevel`
- The doc examples in `collection.rs` should be updated to use the new import path
- The Rust crate must compile successfully
- The existing `SearchPayload` re-export should remain unchanged

## Verification

After your changes, a user should be able to write:

```rust
use chroma::types::ReadLevel;
```

Instead of:

```rust
use chroma_types::plan::ReadLevel;
```
