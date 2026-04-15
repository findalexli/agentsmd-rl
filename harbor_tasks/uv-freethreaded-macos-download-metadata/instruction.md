# Bug: Free-threaded macOS Python downloads produce incorrect metadata

## Summary

The Python download metadata generator (`crates/uv-python/fetch-download-metadata.py`) produces incorrect download entries for **free-threaded** CPython builds on **macOS**.

When the upstream NDJSON feed provides artifacts whose `platform` field contains a build-option suffix (e.g. `aarch64-apple-darwin-freethreaded`), the parser fails to extract the freethreaded build option from the platform string. This causes:

1. The `build_options` list on the returned `PythonDownload` object does **not** contain `"freethreaded"` — it should.
2. The `variant` attribute is `None` instead of `Variant.FREETHREADED`.
3. The `triple` attribute for a freethreaded build differs from the corresponding non-freethreaded build of the same architecture (they should be equal).
4. Download priority selection mixes up which URL belongs to the default entry and which belongs to the free-threaded entry.

## Relevant module API

The script defines these types used in parsing:

- **`Version(major: int, minor: int, patch: int, prerelease: str)`** — version constructor. Examples: `Version(3, 15, 0, "a7")`, `Version(3, 14, 3, "")`, `Version(3, 13, 0, "rc2")`.
- **`Variant`** — enum with at least `FREETHREADED` and `DEBUG` members.
- **`CPythonFinder`** — class whose parsing method takes a `Version`, a build-date integer, and an artifact dict, and returns a `PythonDownload` object with these attributes:
  - `build_options: list[str]` — build options extracted from the artifact
  - `variant: Variant | None` — the resolved variant enum value
  - `triple` — the platform triple

## Symptom details

When parsing an artifact dict with `"platform": "aarch64-apple-darwin-freethreaded"` and `"variant": "install_only_stripped"`:

- `result.build_options` does **not** contain `"freethreaded"` (it should)
- `result.variant` is `None` instead of `Variant.FREETHREADED`
- `result.triple` differs from the triple returned when parsing `"platform": "aarch64-apple-darwin"` with the same version (they should match)

The same issue affects both `aarch64-apple-darwin-freethreaded` and `x86_64-apple-darwin-freethreaded` across all CPython versions that offer free-threaded builds (3.13+).

## Expected behavior

The parser should recognize `-freethreaded` as a platform suffix on macOS (in addition to the already-handled `-debug` suffix), strip it from the platform string, and include `"freethreaded"` in `build_options` — so that `variant` is correctly set to `Variant.FREETHREADED` and `triple` matches the non-freethreaded counterpart. The existing `-debug` suffix handling must continue to work correctly as a regression constraint: debug artifacts should still have `"debug"` in `build_options` and `variant == Variant.DEBUG`. Linux platform triples (e.g. `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`, `x86_64_v3-unknown-linux-gnu`) must remain unaffected with `variant` set to `None`.
