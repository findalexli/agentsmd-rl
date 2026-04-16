# Task: Update moby/spdystream to fix race conditions and goroutine leaks

## Problem Description

The containerd repository vendors `github.com/moby/spdystream` at version v0.2.0, which contains several race conditions and goroutine leaks. These issues were fixed in v0.5.0.

## Symptoms of the Bug

The vendored spdystream library has these issues:

1. **Race condition in ping handling**: The `Connection.Ping()` method and `handlePingFrame()` access `pingChans` map concurrently without proper synchronization, leading to data races.

2. **Race condition in IsFinished()**: The `Stream.IsFinished()` method reads the `finished` field without acquiring `finishLock`, causing races with concurrent writes.

3. **Goroutine leak in shutdown**: The `shutdown()` method uses `time.AfterFunc` which creates a goroutine that may never terminate, leaking resources.

4. **Timer resource leak**: The `shutdown()` and `Wait()` methods use `time.After()` without stopping the timer, wasting resources.

## Relevant Files

The fix involves these files:
- `go.mod` - Update the dependency version
- `go.sum` - Update checksums
- `vendor/github.com/moby/spdystream/connection.go` - Apply race fixes
- `vendor/github.com/moby/spdystream/stream.go` - Apply race fix
- `vendor/modules.txt` - Update version reference
- `integration/client/go.sum` - Update checksums

## What You Need to Do

1. Update `go.mod` to reference `github.com/moby/spdystream v0.5.0`
2. Run `go mod tidy` to update `go.sum`
3. Run `go mod vendor` to update the vendored files
4. Verify the race fixes are present in the vendored files:
   - `pingLock` protecting both `pingId` and `pingChans`
   - Proper lock/defer pattern for pingChans deletion
   - `IsFinished()` using `finishLock`
   - No `time.AfterFunc` usage (replaced with `NewTimer` + `defer Stop`)

## Hints

- The PR is a dependency update from v0.2.0 to v0.5.0
- Look at the spdystream changelog for v0.5.0 to understand the fixes
- The key issues are around the `pingLock` (formerly `pingIdLock`), `finishLock`, and timer usage patterns
- After updating go.mod, use `go mod vendor` to bring in the updated code
