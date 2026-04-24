# Direct URLs with different hash fragments are treated as different versions

## Problem

When two direct URLs point to the exact same package archive but carry different hash fragments (e.g., one uses `#sha256=...` and the other uses `#sha512=...`), they are incorrectly treated as two distinct "versions" by the `VersionId` type in the distribution-types crate.

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

## Implementation Notes

- The `VersionId` type is defined in `crates/uv-distribution-types/src/id.rs`.
- `VersionId::from_url` accepts a `DisplaySafeUrl` argument (from the `uv_redacted` crate).
- Code in `id.rs` should not use `.unwrap()` in production code; prefer `.expect()` with a descriptive message. See AGENTS.md line 7 for the project's convention on this.

## API Under Test

The test suite calls `VersionId::from_url` with URLs parsed via `DisplaySafeUrl::parse(url).unwrap()`. Your implementation must ensure this API produces equal `VersionId` values for archive URLs that differ only in hash fragments, while preserving subdirectory semantics.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`
