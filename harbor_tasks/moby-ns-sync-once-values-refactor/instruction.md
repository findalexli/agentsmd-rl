# Refactor daemon/libnetwork/ns namespace initialization

The `daemon/libnetwork/ns` package uses a global state pattern with `sync.Once` for lazy initialization of namespace handles. This pattern relies on global mutable variables which is problematic for code using these handles concurrently.

## Problems to fix

### 1. `daemon/libnetwork/ns/init_linux.go`

The current implementation has several issues that cause problems at runtime and during code review:

- Global variables `initNs`, `initNl`, and `initOnce` manage lazy initialization, but the mutable `initNs` and `initNl` variables are shared across goroutines without proper synchronization
- `NetlinkSocketsTimeout` is declared as a `var` but is never modified after initialization (it should be a constant)
- `ParseHandlerInt()` returns an `int` from the namespace handle, but callers actually need the `netns.NsHandle` type directly — this causes type safety issues
- Error logging uses unstructured `Errorf` with `%v` formatting instead of the structured logging API (`WithError`)
- `syscall.Close()` return values are silently ignored, which can mask errors during socket cleanup

The refactoring should eliminate global mutable state. The package should provide a clean API for accessing the initial namespace and netlink handles.

### 2. `daemon/libnetwork/ns/init_windows.go`

This Windows stub file exists only to make `go build ./...` work on Windows, but the package contains no actual Windows-specific code. The stub should be removed.

### 3. `daemon/libnetwork/osl/interface_linux.go`

This file calls into the `ns` package in two locations to get a namespace handle for `LinkSetNsFd`. The current implementation returns an `int` from the namespace handle, but `LinkSetNsFd` needs an `int` file descriptor — so callers must cast. The API should provide the `netns.NsHandle` type directly so callers can cast explicitly where needed.

## Verification

After refactoring:
- `go build ./daemon/libnetwork/ns/...` should succeed
- `go vet ./daemon/libnetwork/ns/...` should pass
- `go test ./daemon/libnetwork/ns/...` should pass
- `go build ./daemon/libnetwork/osl/...` should succeed
