# fs.stat throws EPERM under seccomp on Linux

## Problem

On Linux, `fs.stat()`, `fs.lstat()`, and `fs.fstat()` throw `EPERM` when running under seccomp filters that don't whitelist the `statx` syscall. This happens with:
- libseccomp < 2.3.3
- Docker < 18.04 (default seccomp profile)
- Various CI sandboxes and minimal container runtimes

Node.js/libuv handles this gracefully by falling back to `fstatat`, but Bun crashes with `EPERM`.

Additionally, on some QEMU user-mode and S390 RHEL Docker setups, `statx` returns an abnormal positive return code (not 0 for success, not `-errno` for failure), which is also not handled.

## Expected Behavior

`fs.stat()`, `fs.lstat()`, and `fs.fstat()` should succeed even when `statx` is blocked by seccomp, by falling back to `fstat`/`lstat`/`stat` — matching libuv's behavior which falls back on `EPERM`, `EINVAL`, `ENOSYS`, and `EOPNOTSUPP`.

## Files to Look At

- `src/sys.zig` — contains `statxImpl` which handles the `statx` syscall with fallback logic. The current fallback only triggers on `ENOSYS` and `EOPNOTSUPP`, missing `EPERM` and `EINVAL`. The abnormal positive `rc` case is also not handled.
