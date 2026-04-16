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

## Requirements

1. **Error visibility**: Every security scanner error path must print a descriptive error message to stderr before exiting. Currently only `SecurityScannerInWorkspace` errors produce output; all other error variants silently exit. The error handling must cover at least 3 named error variants (such as `InvalidPackageID`, `PartialInstallFailed`, `NoPackagesInstalled`, `SecurityScannerInWorkspace`) OR use a dynamic catch-all pattern that preserves error names via `@errorName`.

2. **Error printing function**: Error messages must use `Output.errGeneric` (not `Output.pretty` with `<red>` formatting). All error printing for security scanner failures must be centralized in `install_with_manager.zig` — the error printing calls (`Output.errGeneric`, `Output.pretty`) must be removed from `security_scanner.zig` for the error variants `InvalidPackageID`, `PartialInstallFailed`, `NoPackagesInstalled`, and `SecurityScannerInWorkspace`.

3. **Error propagation**: When the retry result contains an `.error` variant, the original error information must be preserved and propagated rather than being collapsed into a generic `SecurityScannerRetryFailed` error. The implementation should handle the `.error` variant explicitly (e.g., via `.error => |e|` or `inline else => |e|` pattern) instead of using `else => return error.SecurityScannerRetryFailed`.

4. **Regression test**: Create a regression test at `test/regression/issue/28193.test.ts` that:
   - Imports `bunExe`, `bunEnv`, and `tempDir` from the `'harness'` module using the exact syntax `from "harness"`
   - Does NOT use `tmpdirSync` or `mkdtempSync` from Node.js
   - Contains at least one test case with `expect()` assertions
   - Has more than 5 lines of content
   - Follows CLAUDE.md guideline #101: assert stderr/stdout content before asserting exit code

## Files to Investigate

- `src/install/PackageManager/install_with_manager.zig` — security scanner error handling in the install flow; should contain centralized error printing for all security scanner errors
- `src/install/PackageManager/security_scanner.zig` — security scanner implementation and error returns; should NOT contain error printing calls for `InvalidPackageID`, `PartialInstallFailed`, `NoPackagesInstalled`, or `SecurityScannerInWorkspace`
