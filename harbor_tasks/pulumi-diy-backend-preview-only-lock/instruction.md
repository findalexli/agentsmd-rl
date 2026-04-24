# Task: Fix State Lock Behavior for Preview-Only Refresh

## Problem

The `pulumi refresh --preview-only` command in the DIY backend incorrectly acquires a state lock even though no actual state changes occur during preview-only mode. This creates unnecessary contention and can cause operations to block when they shouldn't.

When `Refresh` is called with `PreviewOnly=true` (the field is accessed via `op.Opts.PreviewOnly`), the state lock should NOT be acquired because preview-only operations don't modify state. When `PreviewOnly=false` (actual refresh), the state lock should be acquired to protect state modifications.

## Files to Modify

- `pkg/backend/diy/backend.go` — the `Refresh` function

## Required Elements

The `Refresh` function in the DIY backend contains these elements:
- `op.Opts.PreviewOnly` — the boolean field indicating preview-only mode
- `b.Lock(ctx, stack.Ref())` — the state lock acquisition
- `b.Unlock(ctx, stack.Ref())` — the state lock release
- `backend.ApplierOptions{` — options for the preview handling code path

The fix must ensure the state lock is only acquired when performing an actual refresh (not in preview-only mode).

## Verification

After your changes:
- `go build ./backend/diy/...` should succeed
- `go test ./backend/diy/...` should pass
- `go vet ./backend/diy/...` should pass
- `go fmt ./backend/diy/...` should produce no changes
- The `Refresh` function should only acquire the state lock when performing an actual refresh (not preview-only)

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `golangci-lint (Go linter)`
