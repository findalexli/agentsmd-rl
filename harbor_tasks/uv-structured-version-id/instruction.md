# Direct URLs with different hash fragments are treated as different versions

## Problem

When two direct URLs point to the exact same package archive but carry different hash fragments (e.g., one uses `#sha256=...` and the other uses `#sha512=...`), they are incorrectly treated as two distinct "versions" by the `VersionId` type in `crates/uv-distribution-types/src/id.rs`.

For example, these two URLs refer to the same artifact but produce different `VersionId` values:

```text
https://files.pythonhosted.org/packages/.../anyio-4.0.0-py3-none-any.whl#sha256=cfdb2b...
https://files.pythonhosted.org/packages/.../anyio-4.0.0-py3-none-any.whl#sha512=f30761...
```

The same class of issue affects Git URLs: irrelevant fragments like `egg=pkg` in the URL hash cause two otherwise-identical Git source references to be considered different.

## Expected Behavior

`VersionId` should use structured, kind-aware identity semantics:

- **Archive URLs**: identity should be based on the URL location and optional `subdirectory` parameter only — hash algorithm/digest fragments should be ignored.
- **Git URLs**: identity should be based on the repository URL, reference, and optional `subdirectory` — irrelevant fragments like `egg=` should be ignored.
- **Local paths and directories**: identity should be based on the resolved file path and its kind (file vs. directory).

Two URLs that refer to the same source should always produce equal `VersionId` values regardless of which verification hash is attached.

## Files to Look At

- `crates/uv-distribution-types/src/id.rs` — defines `VersionId` and its constructors (`from_url`, `from_name_version`) and `Display` implementation
- `crates/uv-distribution-types/src/lib.rs` — `DistributionMetadata` trait implementations that produce `VersionId` values
- `crates/uv-distribution-types/src/cached.rs` — cached distribution metadata
- `crates/uv-distribution-types/src/requested.rs` — requested distribution metadata
- `crates/uv-distribution-types/src/resolved.rs` — resolved distribution metadata
