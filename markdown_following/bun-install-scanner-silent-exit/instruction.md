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

The same silent exit happens for various other scanner failure modes.

## Requirements

1. **Error visibility**: Every security scanner error path must print a descriptive error message to stderr before exiting. Currently some error variants produce output while others silently exit. The implementation must ensure all error paths are covered.

2. **Error printing function**: Error messages must use an appropriate error output function from the `Output` module (such as `Output.errGeneric`). Error printing for security scanner failures should be centralized in the install manager where errors are caught, rather than scattered across multiple files.

3. **Error propagation**: When the security scanner returns an error result, the original error information should be preserved and propagated rather than being collapsed into a single generic error. The result handling should explicitly match all result variants.

4. **Regression test**: Create a regression test following the project's convention for issue-numbered test files that:
   - Imports `bunExe`, `bunEnv`, and `tempDir` from the `'harness'` module using the exact syntax `from "harness"`
   - Does NOT use `tmpdirSync` or `mkdtempSync` from Node.js
   - Contains at least one test case with `expect()` assertions
   - Has more than 5 lines of content
   - Follows the guideline that asserts stderr/stdout content before asserting exit code

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
