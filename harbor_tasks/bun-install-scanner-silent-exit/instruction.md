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

1. **Error visibility**: Every security scanner error path must print a descriptive error message to stderr before exiting. Currently only `SecurityScannerInWorkspace` errors produce output; all other error variants silently exit.

2. **Error printing function**: Error messages must use `Output.errGeneric` (not `Output.pretty` with `<red>` formatting).

3. **Error propagation**: When the retry result contains an `.error` variant, the original error information must be preserved and propagated rather than being collapsed into a generic `SecurityScannerRetryFailed` error.

4. **Regression test**: Create a regression test at `test/regression/issue/28193.test.ts` that:
   - Imports `bunExe`, `bunEnv`, and `tempDir` from the `'harness'` module
   - Does NOT use `tmpdirSync` or `mkdtempSync` from Node.js
   - Contains at least one test case with `expect()` assertions
   - Follows CLAUDE.md guideline #101: assert stderr/stdout content before asserting exit code

## Files to Investigate

- `src/install/PackageManager/install_with_manager.zig` — security scanner error handling in the install flow
- `src/install/PackageManager/security_scanner.zig` — security scanner implementation and error returns
