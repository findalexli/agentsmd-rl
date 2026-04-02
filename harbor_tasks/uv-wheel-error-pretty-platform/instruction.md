# Bug: Platform names in wheel compatibility errors are not human-friendly

When `uv` builds a wheel and discovers it is incompatible with the current (or target) platform, it prints an error like:

```
The built wheel `foo-1.0.0-cp315-abi3t-macosx_11_0_arm64.whl` is not compatible with the current Python 3.15 on macos aarch64
```

The platform portion of this message uses the raw internal representation of the OS (e.g., `macos` instead of `macOS`, `manylinux` instead of `Linux`). Additionally, the OS and architecture are passed as two separate format arguments, which makes the formatting fragile and inconsistent.

## Expected behavior

The error message should display platform names in proper human-readable form:

- `macos` → `macOS`
- `manylinux` / `musllinux` → `Linux`
- `windows` → `Windows`
- `freebsd` → `FreeBSD`
- `netbsd` → `NetBSD`
- `openbsd` → `OpenBSD`
- etc.

For example:
```
The built wheel `foo-1.0.0-cp315-abi3t-macosx_11_0_arm64.whl` is not compatible with the current Python 3.15 on macOS aarch64
```

## Relevant files

- `crates/uv-platform-tags/src/platform.rs` — the `Platform` struct and its `os()` / `arch()` accessors
- `crates/uv-distribution/src/error.rs` — the `BuiltWheelIncompatibleHostPlatform` and `BuiltWheelIncompatibleTargetPlatform` error variants, which format the platform in their `#[error(...)]` attributes

## Guidance

The `Platform` struct currently only exposes `os()` and `arch()` individually. There is no method that returns a combined, human-readable platform string. The error variants use `python_platform.os()` and `python_platform.arch()` as separate format arguments.

Consider adding a method to `Platform` that produces a properly-capitalized, combined representation, then use it in the error format strings.
