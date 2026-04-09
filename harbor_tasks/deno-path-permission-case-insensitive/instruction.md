# Case-Insensitive Path Permission Matching on Windows

## Problem

Deno's permission system uses case-sensitive path comparison for all platforms, including Windows. On Windows (NTFS), the filesystem is case-insensitive, so `C:\Users\Admin\file.txt` and `c:\users\admin\file.txt` refer to the same file. However, Deno's `--allow-read`, `--deny-read` (and similar path-scoped permission flags for write, FFI, etc.) compare paths using exact byte equality.

This means a deny rule like `--deny-read=C:\Users\Admin\Secret` can be bypassed by accessing `c:\users\admin\secret\data.txt` — the lowercase variant doesn't match the deny rule, so the read is allowed.

The same issue affects:
- `PartialEq` comparisons between `PathQueryDescriptor` and `PathDescriptor`
- `Hash` for `PathDescriptor` (case-different paths hash differently, breaking set lookups)
- `starts_with` checks (used for directory-scoped permissions)
- Ordering methods `cmp_allow_allow` and `cmp_allow_deny` (used for allow/deny rule resolution)

## Expected Behavior

On Windows, path permission checks should be case-insensitive. A deny rule for `C:\Users\Admin\Secret` must also block access via `c:\users\admin\secret` or any other case variant. On non-Windows platforms, behavior should remain unchanged (case-sensitive).

## Files to Look At

- `runtime/permissions/lib.rs` — Contains `PathQueryDescriptor`, `PathDescriptor`, and all path comparison/hashing/ordering logic for the permission system
