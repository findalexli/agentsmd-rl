# Bug: Free-threaded macOS Python downloads mapped to wrong URLs

## Summary

The Python download metadata generator (`crates/uv-python/fetch-download-metadata.py`) produces incorrect download entries for **free-threaded** CPython builds on **macOS**.

When the upstream NDJSON feed provides artifacts whose `platform` field contains a build-option suffix (e.g. `aarch64-apple-darwin-freethreaded`), the parser only recognizes and strips the `-debug` suffix. The `-freethreaded` suffix is left in the platform string, which means:

1. The "freethreaded" build option is never extracted from the platform, so the resulting `Variant` is `None` instead of `FREETHREADED`.
2. Because the variant is wrong, download priority selection mixes up which URL belongs to the default (non-free-threaded) entry and which belongs to the free-threaded entry.
3. The generated `download-metadata.json` ends up with incorrect URLs and SHA256 hashes for affected macOS entries — default entries point to free-threaded archives and vice versa.

## Affected code

- `crates/uv-python/fetch-download-metadata.py` — the `_parse_ndjson_artifact` method in `CPythonFinder`, specifically the block that strips platform suffixes (around line 296).

## How to reproduce

Parse an NDJSON artifact with `"platform": "aarch64-apple-darwin-freethreaded"` and `"variant": "install_only_stripped"`. Observe that:
- `build_options` does **not** contain `"freethreaded"`
- The returned `PythonDownload.variant` is `None` instead of `Variant.FREETHREADED`

The same issue affects both `aarch64` and `x86_64` macOS triples, across all CPython versions that offer free-threaded builds (3.13+).

## Expected behavior

The parser should recognize `-freethreaded` (in addition to `-debug`) as a platform suffix on macOS, strip it from the platform string, and promote it to a build option — so the variant is correctly set and the right URL is associated with each entry.
