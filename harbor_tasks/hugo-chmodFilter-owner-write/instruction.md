# Fix Permission Syncing for Read-Only Source Files

## Problem

When Hugo syncs static files to the `/public` output directory, file permissions are copied from source to destination. Files from the Go Module cache typically have read-only permissions (mode `0444`), and these restrictive permissions get synced to the published files, making them write-protected and inconvenient for users.

The `chmodFilter` function in `commands/server.go` controls whether permission syncing should be skipped for a given file. Currently it only skips syncing for directories.

## Requirements

1. Modify the `chmodFilter` function in `commands/server.go` to also skip permission syncing for source files whose permissions do not include the owner-write permission bit (the bit with value `0o200` in Go permission notation).

2. Preserve the existing behavior of skipping permission syncing for directories.

3. Update the function's documentation comment to reference the owner-write permission.

## Expected Behavior

| Source | Permissions | Permission sync |
|---|---|---|
| Directory | any | skipped |
| Regular file | no owner-write (e.g. `0444`) | skipped |
| Regular file | has owner-write (e.g. `0644`) | synced normally |

## Verification

After making changes, verify the project compiles and passes `go vet`, `staticcheck`, and `gofmt` checks on the `commands` package.