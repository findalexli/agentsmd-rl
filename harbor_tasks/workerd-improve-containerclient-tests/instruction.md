# Improve container-client test reliability and documentation

## Problem

The container-client tests in `src/workerd/server/tests/container-client/test.js` have several reliability issues:

1. **WebSocket test can hang forever**: The WebSocket interception test creates a Promise to wait for a WebSocket message, but there's no timeout mechanism. If the message never arrives, the test hangs indefinitely with no useful error. The fix should use `Promise.withResolvers()` and a 5_000 millisecond timeout that rejects with an error message like "Websocket message not received within 5 seconds".

2. **Noisy retry logging**: The TCP port retry loop logs verbose `console.info` messages on every retry attempt, including lines containing the text `Retrying getTcpPort`. This clutters test output and makes it harder to spot real failures. Remove the per-retry console.info messages.

3. **README has incorrect commands**: The test README at `src/workerd/server/tests/container-client/README.md` contains commands that are either broken or incorrect:
   - The container cleanup command uses a `$()` subshell that errors when no matching containers exist
   - The test run command is missing the required Bazel target suffix `:container-client@`

## Expected Behavior

- The WebSocket promise code should use `Promise.withResolvers()` with a 5_000 millisecond timeout so it fails with a clear error message instead of hanging
- The retry loop must not log verbose info messages containing "Retrying getTcpPort" on each retry attempt
- The README should have correct, safe-to-run commands:
  - Use pipe-based docker cleanup (e.g., `docker ps ... | xargs -r docker rm -f`) instead of subshell `$()`
  - Bazel target name must include the `:container-client@` suffix (e.g., `//src/workerd/server/tests/container-client:container-client@`)

## Files to Look At

- `src/workerd/server/tests/container-client/test.js` — the container-client test suite (Durable Object tests)
- `src/workerd/server/tests/container-client/README.md` — instructions for running these tests locally

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
- `prettier (JS/TS/JSON/Markdown formatter)`
