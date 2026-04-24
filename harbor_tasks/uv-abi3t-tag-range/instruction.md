# Free-threaded CPython missing abi3t tags for lower Python versions

## Problem

When generating platform compatibility tags for free-threaded CPython builds (e.g., CPython 3.13t or 3.15t), `uv` only emits `abi3t` tags starting from Python 3.15. This means:

- A free-threaded CPython 3.15 build only gets `cp315-abi3t` but not `cp314-abi3t`, `cp313-abi3t`, ..., `cp32-abi3t`
- A free-threaded CPython 3.13 build gets **zero** `abi3t` tags at all (since 3.13 < 3.15)

This is incorrect. The `abi3t` tags should be emitted for every abi3-compatible version (3.2 through the current version), mirroring how `abi3` tags work for non-free-threaded builds. A wheel tagged `abi3t` for Python 3.2 should be considered compatible with any free-threaded CPython >= 3.2.

## Expected Behavior

For a free-threaded CPython 3.15 build, the tag list should include `abi3t` entries for `cp315` down to `cp32` — the same range that `abi3` covers for non-free-threaded builds.

Similarly, a free-threaded CPython 3.13 build should include `abi3t` entries for `cp313` down to `cp32`.

## Files to Look At

- `crates/uv-platform-tags/src/tags.rs` — the `from_env` method on `Tags` generates the ordered list of compatible platform tags, including the `abi3`/`abi3t` section

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`
