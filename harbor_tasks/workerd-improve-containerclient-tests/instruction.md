# Improve container-client test reliability and documentation

## Problem

The container-client tests in `src/workerd/server/tests/container-client/test.js` have several reliability issues:

1. **WebSocket test can hang forever**: The `testInterceptWebSocket` method creates a Promise to wait for a WebSocket message, but there's no timeout. If the message never arrives, the test hangs indefinitely with no useful error. The promise creation code is bracketed by comments `// Listen for response` and `// Send a test message` within the test method.

2. **Noisy retry logging**: The TCP port retry loop logs verbose `console.info` messages on every retry attempt, including the full error object. This clutters test output and makes it harder to spot real failures.

3. **README has incorrect commands**: The test README at `src/workerd/server/tests/container-client/README.md` contains commands that are either broken or incorrect:
   - The container cleanup command uses a `$()` subshell that errors when no matching containers exist
   - The test run command is missing the required Bazel target suffix `:container-client@`

## Expected Behavior

- The WebSocket test should use a modern promise pattern with a timeout so it fails clearly instead of hanging
- Retry logging should only report actual failures, not every retry attempt
- The README should have correct, safe-to-run commands

## Files to Look At

- `src/workerd/server/tests/container-client/test.js` — the container-client test suite (Durable Object tests)
- `src/workerd/server/tests/container-client/README.md` — instructions for running these tests locally

After fixing the code, update the README to reflect the correct commands. The Bazel target name must include the `:container-client@` suffix (e.g., `//src/workerd/server/tests/container-client:container-client@`).
