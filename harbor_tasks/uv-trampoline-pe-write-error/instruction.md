# Improve error reporting in uv-trampoline-builder

## Bug

When `write_resources` in `crates/uv-trampoline-builder/src/lib.rs` fails to update Windows PE resources (via `BeginUpdateResourceW`, `UpdateResourceW`, or `EndUpdateResourceW`), the error is mapped to a generic `Error::Io`. This loses the context of **which file** the operation was targeting, making it difficult to debug failures like the one reported in issue #18663.

The `Error` enum in this crate has several well-typed variants (e.g., `InvalidPath`, `UnsupportedWindowsArch`), but `write_resources` falls back to the blanket `Io` variant even though it has the file path available.

## Expected behavior

When a Windows PE resource write fails, the error message should include the path of the file being modified, so users and logs can identify exactly which file caused the problem.

## Relevant files

- `crates/uv-trampoline-builder/src/lib.rs` — the `Error` enum and `write_resources` function
- `crates/uv-trampoline-builder/Cargo.toml` — crate dependencies
