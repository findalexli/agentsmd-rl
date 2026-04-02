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

## Scope

The three install paths (package, bundle, file) all need the same treatment.
The existing test file `src/plugins/install.test.ts` has cases that assert
`result.ok` is `true` after scan warnings — these need to be updated to assert
blocking behavior.
