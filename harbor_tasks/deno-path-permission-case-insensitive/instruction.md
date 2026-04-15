# Case-Insensitive Path Permission Matching on Windows

## Problem

Deno's permission system uses case-sensitive path comparison for all platforms, including Windows. On Windows (NTFS), the filesystem is case-insensitive, so `C:\Users\Admin\file.txt` and `c:\users\admin\file.txt` refer to the same file. However, Deno's `--allow-read`, `--deny-read` (and similar path-scoped permission flags for write, FFI, etc.) compare paths using exact byte equality.

This means a deny rule like `--deny-read=C:\Users\Admin\Secret` can be bypassed by accessing `c:\users\admin\secret\data.txt` — the lowercase variant doesn't match the deny rule, so the read is allowed.

## Expected Behavior

On Windows, path permission checks should be case-insensitive. A deny rule for `C:\Users\Admin\Secret` must also block access via `c:\users\admin\secret` or any other case variant. On non-Windows platforms, behavior should remain unchanged (case-sensitive).

The permission system lives in `runtime/permissions/lib.rs`.

## Requirements

The fix requires the following structural elements in `runtime/permissions/lib.rs`:

1. **A helper function** that produces a canonical path for comparison, accepting a `&Path` and returning a `PathBuf`. On Windows it normalizes case (using ASCII case folding); on other platforms it returns the path unchanged.

2. **Both `PathQueryDescriptor` and `PathDescriptor` structs** must store this canonical path alongside the original path, in a field of type `PathBuf`.

3. **All comparison operations** — equality (`PartialEq`), hashing (`Hash`), prefix checking (`starts_with`), and ordering (`cmp_allow_allow`, `cmp_allow_deny`) — must use the canonical path field, not the raw path field, when performing comparisons.
