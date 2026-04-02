# Bug: Dynamic metadata field values matched case-sensitively

## Context

`uv` reads Python package metadata from `PKG-INFO` and `METADATA` files. When a source distribution's `PKG-INFO` file lists certain fields as `Dynamic` (meaning their values aren't finalized until build time), `uv` rejects the static metadata and falls back to building the package.

The relevant code is in `crates/uv-pypi-types/src/metadata/metadata_resolver.rs`, in the `parse_pkg_info` and `parse_metadata` methods of `ResolutionMetadata`.

## The Bug

The `Dynamic` field value comparison uses exact (case-sensitive) string matching. For example, `parse_pkg_info` checks for `"Requires-Dist"`, `"Requires-Python"`, `"Provides-Extra"`, and `"Version"` using a `match` statement with literal strings. Similarly, `parse_metadata` checks `field == "Version"`.

However, some real-world packages emit `Dynamic` field values in non-canonical casing (e.g., `requires-dist` instead of `Requires-Dist`). The `packaging` library from PyPA treats these values case-insensitively. Because `uv` does exact matching, these lowercase variants silently slip through undetected — `uv` doesn't recognize that the field is actually dynamic, and proceeds to use the static metadata as if it were complete. This can lead to incorrect dependency resolution when the static metadata is stale or incomplete.

This affects both `parse_pkg_info` (which should reject packages with dynamic `Requires-Dist`, `Requires-Python`, or `Provides-Extra` regardless of casing) and `parse_metadata` (which should detect dynamic `Version` regardless of casing).

## Expected Behavior

Dynamic field value matching should be case-insensitive, consistent with how the `packaging` library handles these values. A `Dynamic: requires-dist` header should be treated the same as `Dynamic: Requires-Dist`.
