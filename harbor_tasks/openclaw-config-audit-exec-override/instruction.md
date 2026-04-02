# Missing audit coverage for exec tool re-enabled over HTTP

## Problem

The security config audit (`src/security/audit.ts`) correctly detects when dangerous tools are re-enabled via `gateway.tools.allow` on a non-loopback HTTP surface and raises a `gateway.tools_invoke_http.dangerous_allow` finding. The test suite in `src/security/audit.test.ts` verifies this behavior for tools like `sessions_spawn` and `gateway`, but it has no coverage for `exec` — one of the most dangerous tools in the deny list since it provides direct command execution (immediate RCE surface).

An operator could add `exec` to their `gateway.tools.allow` config with a LAN-facing bind, and while the audit *does* flag it at runtime, there is no regression test proving this. If someone accidentally removed `exec` from the deny list in a future refactor, the test suite would not catch it.

## What needs to happen

Add a test case to the existing `"scores dangerous gateway.tools.allow over HTTP by exposure"` test in `src/security/audit.test.ts` that:

1. Configures `gateway.tools.allow` to include `exec` with a non-loopback bind and auth token
2. Asserts the audit produces a finding with `critical` severity

Look at the existing test cases in that block for the exact pattern — they use `runConfigAuditCases` with a config object and `expectedSeverity`.

## Relevant files

- `src/security/audit.test.ts` — the test file to modify
- `src/security/audit.ts` — the audit logic (for context, not to change)
- `src/security/dangerous-tools.ts` — the deny list constant (for context)
