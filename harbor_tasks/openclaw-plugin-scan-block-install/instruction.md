# Bug: Plugin install continues after security scan finds critical patterns or fails

## Summary

When installing a plugin (via package, bundle, or plain file), the install-time
security source scan can detect dangerous code patterns (critical findings) or
fail outright. In both cases the install currently **continues anyway**, only
logging a warning. This defeats the purpose of the scan — a plugin with
`eval('danger')` in its source still gets installed.

The expected behavior:

1. If the builtin source scan finds **critical** patterns, the install should
   be **blocked** and return an error describing what was detected.
2. If the builtin source scan **fails** (throws), the install should be
   **blocked** and return an error mentioning the scan failure.
3. The `before_install` hook may still override the outcome — if a hook
   explicitly blocks, the hook's block takes precedence. But if the hook does
   not block, the builtin scan's block should still be enforced.
4. The blocked result should carry a machine-readable error code so callers can
   distinguish "blocked by scan findings" from "blocked by scan failure".

## Affected files

- `src/plugins/install-security-scan.runtime.ts` — the scan runtime that runs
  the builtin scan and the `before_install` hook. Currently returns the hook
  result directly even when the builtin scan found critical issues.
- `src/plugins/install-security-scan.ts` — the type definition for
  `InstallSecurityScanResult`. Needs a field to carry the block code.
- `src/plugins/install.ts` — the install orchestrator that calls the scan and
  decides whether to continue. Currently logs warnings and continues on scan
  exceptions instead of blocking.

## Reproduction

Install a plugin whose source contains `eval('danger')`. The scan warns but
the install succeeds. After the fix, the install should fail with a clear
error code and message.

## Required changes

### Error codes

The `PLUGIN_INSTALL_ERROR_CODE` constant in `src/plugins/install.ts` must be
extended with two new entries:

- `SECURITY_SCAN_BLOCKED` with string value `"security_scan_blocked"`
- `SECURITY_SCAN_FAILED` with string value `"security_scan_failed"`

Each code must be used in actual handling logic (not just defined), appearing
at least twice in the file.

### install.ts: catch blocks

In the three install functions (package, bundle, file), the catch blocks that
handle scan exceptions currently log a warning and continue. After the fix,
these catch blocks must return a blocking result with `ok: false`, a descriptive
`error` string, and the `SECURITY_SCAN_FAILED` error code. The string
`"Installation continues"` must not appear anywhere in the file after the fix.

### install-security-scan.ts: type update

The `InstallSecurityScanResult` type's `blocked` object must have a `code`
field with the closed union type `"security_scan_blocked" | "security_scan_failed"
| undefined`.

### install-security-scan.runtime.ts: block construction

The runtime must produce blocked results with the appropriate code based on
the builtin scan outcome:

- When the builtin scan has `status === "error"` → blocked result code is
  `"security_scan_failed"`
- When the builtin scan has `critical > 0` → blocked result code is
  `"security_scan_blocked"`

The scan functions must not directly return the hook result. Instead, they
must capture the hook result and use the builtin block as a fallback when
the hook does not block — applying `hookResult?.blocked ? hookResult : builtinBlocked`
or equivalent logic.

## Scope

The three install paths (package, bundle, file) all need the same treatment.
The existing test file `src/plugins/install.test.ts` has cases that assert
`result.ok` is `true` after scan warnings — these need to be updated to assert
blocking behavior.