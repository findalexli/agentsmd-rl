# Bug: `bun install` silently exits with code 1 when security scanner encounters an error

## Summary

When the security scanner configured in `bunfig.toml` encounters an error during `bun install`, the process silently exits with code 1 without printing any diagnostic message. This makes failures impossible to debug, especially in CI environments where there is no interactive terminal to investigate.

## Reproduction

Configure a security scanner in `bunfig.toml` that cannot be found or is invalid:

```toml
[install.security]
scanner = "@nonexistent-scanner/does-not-exist"
```

Then run:

```bash
bun install
```

**Expected**: An error message explaining why the install failed (e.g., "security scanner failed: ...").
**Actual**: Process exits with code 1 and no output to stderr — completely silent failure.

The same silent exit happens for various other scanner failure modes: invalid package ID, partial install failure, IPC pipe failures, etc.

## Root Cause

The error handling in `src/install/PackageManager/install_with_manager.zig` has a catch-all `else` branch in the security scanner error switch that calls `Global.exit(1)` without printing any message. Only the `SecurityScannerInWorkspace` error variant has a message — all other errors are swallowed silently.

Additionally, some error messages that DO exist are printed in `src/install/PackageManager/security_scanner.zig` at the point where errors are returned, but the catch-all in the caller ignores them. The error printing is split across two files inconsistently.

## Expected Fix

Ensure that every error path in the security scanner error handler prints a descriptive error message to stderr before exiting. Error messages should be centralized in the caller (`install_with_manager.zig`) rather than scattered across both files. Each error variant should have a specific, helpful message.

Also fix the case where the `.error` variant from the retry result is being collapsed into a generic `SecurityScannerRetryFailed`, losing the original error information.

## Files to Investigate

- `src/install/PackageManager/install_with_manager.zig` — the security scanner error handling switch in `installWithManager`
- `src/install/PackageManager/security_scanner.zig` — error returns from `doPartialInstallOfSecurityScanner`, `ScannerFinder`, and `performSecurityScanAfterResolution`
