# Direct URLs with different hash fragments are treated as different versions

## Problem

When two direct URLs point to the exact same package archive but carry different hash fragments (e.g., one uses `#sha256=...` and the other uses `#sha512=...`), they are incorrectly treated as two distinct "versions" by the `VersionId` type in the `uv-distribution-types` crate.

For example, these two URLs refer to the same artifact but produce different `VersionId` values:

```text
https://files.pythonhosted.org/packages/.../anyio-4.0.0-py3-none-any.whl#sha256=cfdb2b...
https://files.pythonhosted.org/packages/.../anyio-4.0.0-py3-none-any.whl#sha512=f30761...
```

The same class of issue affects Git URLs: irrelevant fragments like `egg=pkg` in the URL hash cause two otherwise-identical Git source references to be considered different.

## Expected Behavior

Two URLs that refer to the same source should always produce equal `VersionId` values regardless of which verification hash or irrelevant fragment is attached. Specifically:

- Archive URLs that differ only in their hash algorithm/digest fragment (e.g., `#sha256=...` vs. `#sha512=...`) should produce equal `VersionId` values. However, the `subdirectory` fragment parameter is semantically meaningful — two archive URLs with different `subdirectory` values should remain distinct.
- Git URLs that differ only in irrelevant fragments (like `egg=`) should produce equal `VersionId` values when their repository, reference, and `subdirectory` all match.

## Notes

- `VersionId::from_url` accepts a `DisplaySafeUrl` argument (from the `uv_redacted` crate).
- Follow the project's coding conventions described in AGENTS.md — in particular, avoid using `.unwrap()` in production (non-test) code; prefer `.expect()` with a descriptive message.

## API Under Test

The test suite calls `VersionId::from_url` with URLs parsed via `DisplaySafeUrl::parse(url).unwrap()`. Your implementation must ensure this API produces equal `VersionId` values for archive URLs that differ only in hash fragments, while preserving subdirectory semantics.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`
