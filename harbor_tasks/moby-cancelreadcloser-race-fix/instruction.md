# Fix Race Condition in Client Package

## Problem

The moby/moby repository at `/workspace/moby` contains a data race in its client package. The `cancelReadCloser` type wraps an `io.Reader` with context cancellation support, created via the `newCancelReadCloser(ctx, rc)` function where `ctx` is a context and `rc` is an `io.ReadCloser`. When a context is cancelled during the construction of this wrapper, the context's cancellation callback may execute concurrently with the ongoing initialization of the wrapper struct, causing a data race detected by Go's race detector.

## Symptoms

Running the race detector reveals:
- `DATA RACE` warnings from Go's race detector
- The race occurs between initialization code and a context cancellation callback that fires before the struct is fully set up
- Potential nil pointer dereference crashes
- Flaky tests under concurrent load

A test `TestNewCancelReadCloserRace` has been added to the repository that reproduces this race condition. It creates `cancelReadCloser` instances via `newCancelReadCloser(ctx, rc)` with already-cancelled contexts in a loop and exercises the race detector.

## Behavior Requirements

Your fix must satisfy all of the following:

1. **No data race**: The test `TestNewCancelReadCloserRace` must pass when run with `go test -race` in the `client/` directory, with no `DATA RACE` warnings in output
2. **Close after context cancel works**: After `cancel()` is called on a context passed to `newCancelReadCloser`, calling `Close()` manually must not cause data races
3. **Close called exactly once**: The underlying resource close must execute exactly one time — even when both the automatic context-cancellation close and multiple manual `Close()` calls occur (e.g., `crc.Close()` called 3 times after `cancel()`), the underlying close must only be called once
4. **Existing tests pass**: The following tests in the `client/` package must continue to pass:
   - `TestEncodePlatforms`
   - `TestOptionWithAPIVersion`
5. **Code quality**: `go vet` and `gofmt -l .` must produce no warnings in the `client/` package
6. **Package builds**: `go build .` must succeed in the `client/` directory

## Testing

Start by running the failing test to observe the race:

```bash
cd /workspace/moby/client
go test -race -run TestNewCancelReadCloserRace -v .
```
