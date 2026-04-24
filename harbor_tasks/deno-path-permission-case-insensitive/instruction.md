# Case-Insensitive Path Permission Matching on Windows

## Problem

Deno's permission system uses case-sensitive path comparison for all platforms, including Windows. On Windows (NTFS), the filesystem is case-insensitive, so `C:\Users\Admin\file.txt` and `c:\users\admin\file.txt` refer to the same file. However, Deno's `--allow-read`, `--deny-read` (and similar path-scoped permission flags for write, FFI, etc.) compare paths using exact byte equality.

This means a deny rule like `--deny-read=C:\Users\Admin\Secret` can be bypassed by accessing `c:\users\admin\secret\data.txt` — the lowercase variant doesn't match the deny rule, so the read is allowed.

## Expected Behavior

On Windows, path permission checks should be case-insensitive. A deny rule for `C:\Users\Admin\Secret` must also block access via `c:\users\admin\secret` or any other case variant. On non-Windows platforms, behavior should remain unchanged (case-sensitive).

## Location

The permission system lives in `runtime/permissions/lib.rs` in the `deno_runtime` crate. This is where path comparison logic is implemented.

## Required Code Changes

The fix requires adding a case-insensitive path representation to the path descriptor types:

- A `cmp_path: PathBuf` field added to both `PathDescriptor` and `PathQueryDescriptor`. On Windows, this stores a lowercased copy of the path; on other platforms it is identical to the original path.
- A `comparison_path(path: &Path) -> PathBuf` helper function that returns the lowercased path on Windows and a direct clone on other platforms.
- The `cmp_path` field is used in `PartialEq`, `Hash`, `starts_with`, and the ordering comparisons, replacing direct use of the `path` field.

## Note on Testing

The bug fix only changes behavior on Windows. Tests run on Linux, so correctness is verified via:
- The Rust code compiles cleanly
- The crate's unit test suite passes
- Code uses the case-insensitive path representation for all comparisons (enforced by the test suite)

On Linux/macOS, the `cmp_path` field is identical to the original path (the case-fold only happens on Windows). This structural change is verified through compilation and the existing test suite.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`
