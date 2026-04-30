# fs.stat throws EPERM under seccomp on Linux

## Problem

On Linux, `fs.stat()`, `fs.lstat()`, and `fs.fstat()` throw `EPERM` when running under seccomp filters that don't whitelist the `statx` syscall. This happens with:
- libseccomp < 2.3.3
- Docker < 18.04 (default seccomp profile)
- Various CI sandboxes and minimal container runtimes

Bun's statx implementation crashes with `EPERM` in these environments, while Node.js/libuv handles the situation gracefully by falling back to legacy syscalls.

Additionally, on some QEMU user-mode and S390 RHEL Docker setups, `statx` returns an abnormal positive return code — neither 0 (success) nor a negative errno value — which is also not handled correctly.

## Expected Behavior

When `statx` is unavailable or blocked, Bun should fall back to legacy syscalls (`fstat`/`lstat`/`stat`) — matching libuv's approach. Per libuv's implementation (see `deps/uv/src/unix/fs.c` in the Node.js codebase), fallback should be triggered for the following errno values:
- `ENOSYS` — kernel older than 4.11
- `EOPNOTSUPP` — filesystem doesn't support statx
- `EPERM` — seccomp filter blocks statx (libseccomp < 2.3.3, Docker < 18.04, CI sandboxes)
- `EINVAL` — old Android builds

The implementation must also handle the abnormal positive return code case, treating it as "statx not available."

## Implementation Notes

The statx syscall wrapper for Linux is in `src/sys.zig`. When implementing the fix:
- Use `bun.sys` API patterns: `Maybe(T)` return type, `.result`/`.err` tagged union handling
- Create a `statxFallback` helper function that consolidates the fallback to legacy syscalls (`stat`/`lstat`/`fstat`)
- Handle both path-based (`stat`/`lstat`) and fd-based (`fstat`) fallback cases within the helper
- Respect the `SYMLINK_NOFOLLOW` flag to choose `lstat` vs `stat` for path-based calls
- Preserve the existing `EINTR` retry loop and `linux.statx` syscall call
- Disable the `supports_statx_on_linux` flag when falling back
- The errno cases should be handled together in a unified manner rather than scattered

## Repository Integrity

The fix must not alter files unrelated to the statx implementation. The following must remain intact:

- `.coderabbit.yaml` — must remain valid YAML with `language` and `reviews` keys
- `.editorconfig` — must retain settings: `root = true`, `charset = utf-8`, `end_of_line = lf`, `trim_trailing_whitespace = true`, `insert_final_newline = true`
- `AGENTS.md` — must remain a symlink pointing to `CLAUDE.md`
- `CLAUDE.md` — must remain present and non-empty
- `build.zig` and `package.json` must remain unchanged

All modified Zig files must pass `zig fmt --check`:
- `src/sys.zig`
- `build.zig`
- `src/bun.zig`
- `src/cli.zig`
