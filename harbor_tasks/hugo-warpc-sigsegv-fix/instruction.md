# Fix SIGSEGV in Close() when warpc dispatcher fails to start

## Problem

When a lazyDispatcher fails to start (e.g., due to invalid WASM module configuration), calling `Close()` on the `Dispatchers` struct causes a SIGSEGV (segmentation fault). This happens because the `started` flag is set to `true` unconditionally in `start()`, even when `Start()` returns an error, leaving `dispatcher` as `nil`.

## Location

The bug is in `internal/warpc/warpc.go` in the `lazyDispatcher.start()` method:

```go
func (d *lazyDispatcher[Q, R]) start() (Dispatcher[Q, R], error) {
    d.startOnce.Do(func() {
        start := time.Now()
        d.dispatcher, d.startErr = Start[Q, R](d.opts)
        d.started = true  // BUG: This is set unconditionally
        d.opts.Infof("started dispatcher in %s", time.Since(start))
    })
    return d.dispatcher, d.startErr
}
```

The `Close()` method correctly checks `if d.katex.started` before calling `d.katex.dispatcher.Close()`, but since `started` is `true` even when start failed, it tries to call `Close()` on a `nil` dispatcher, causing a SIGSEGV.

## Expected Fix

Only set `started = true` when `Start()` succeeds (when `startErr == nil`). This ensures that `Close()` won't attempt to close a `nil` dispatcher.

## Files to Modify

- `internal/warpc/warpc.go`: Fix the `lazyDispatcher.start()` method to only set `started=true` on successful start.

## Related

Fixes issue #14536
