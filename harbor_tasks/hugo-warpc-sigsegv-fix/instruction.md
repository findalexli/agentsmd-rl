# Fix SIGSEGV in Close() when warpc dispatcher fails to start

## Problem

When a lazyDispatcher fails to start (e.g., due to invalid WASM module configuration), calling `Close()` on the `Dispatchers` struct causes a SIGSEGV (segmentation fault). This happens because the `started` flag is set to `true` even when `Start()` returns an error, leaving `dispatcher` as `nil`. The `Close()` method then tries to call `Close()` on a `nil` dispatcher.

## Expected Behavior

After the fix, calling `Close()` on a `Dispatchers` struct should not cause a SIGSEGV even when the dispatcher failed to start. The `started` flag should accurately reflect whether the dispatcher was successfully initialized.

## Files Involved

- `internal/warpc/warpc.go` - Contains the `lazyDispatcher` struct with `start()` method and `Dispatchers` struct with `Close()` method

## Related

Fixes issue #14536
