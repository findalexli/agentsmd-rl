# Node Server Readiness Check Race Condition

## Bug Description

Gradio's Playwright CI tests are intermittently flaky — sometimes the browser navigates to the app URL and finds no content on the page. The root cause appears to be a race condition in how the server readiness is verified.

## Affected Files

- `gradio/node_server.py` — the `verify_server_startup()` function
- `js/tootils/src/app-launcher.ts` — the `launchGradioApp()` function used by Playwright test helpers

## Symptoms

When Gradio starts with SSR mode enabled, it launches a Node.js server alongside the Python (Uvicorn) backend. The test infrastructure detects that the server is "ready" and proceeds to run Playwright tests, but occasionally the page is empty or returns errors because the server wasn't actually ready to handle HTTP requests yet.

## Investigation Notes

The current readiness check in `verify_server_startup()` only verifies that a TCP connection can be established on the server's port. However, the Node SSR server may accept TCP connections (the OS-level socket is listening) before the application layer is ready to serve HTTP responses. This means the health check can succeed prematurely.

Similarly, on the TypeScript side, `launchGradioApp()` resolves its startup promise as soon as it sees the "Running on local URL:" log message in stdout, without verifying that the server actually responds to HTTP requests.

## Expected Behavior

### Python side (`gradio/node_server.py`)

The `verify_server_startup()` function must perform an actual HTTP request instead of just checking TCP connectivity. The readiness semantics should be:

- If the server responds with any HTTP status code **less than 500** (e.g., 200, 302, 404), the server is considered **ready** (return `True`). A 404 or redirect still means the HTTP stack is up and handling requests.
- If the server responds with HTTP status **500 or above**, it is **not ready** (return `False`). A 500 indicates a server error — the app is not functioning.
- If no server is listening on the port, return `False`.
- If a TCP socket accepts the connection but never sends an HTTP response (a bare TCP listener), return `False`.

The existing `attempt_connection()` function in the same file must continue to work correctly after the changes — do not break its existing behavior.

### TypeScript side (`js/tootils/src/app-launcher.ts`)

The `launchGradioApp()` function needs an HTTP-based readiness check that polls the server with HTTP requests rather than relying solely on stdout log messages. The file must contain code that makes HTTP requests using one of Node.js's built-in HTTP APIs — the source must include at least one of the patterns `http.request`, `http.get`, or `fetch(`.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
