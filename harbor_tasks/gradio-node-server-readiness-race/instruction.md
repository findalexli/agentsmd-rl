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

The server readiness check should verify that the server can actually handle HTTP requests, not just that the port is accepting TCP connections. Both the Python-side startup verification and the TypeScript-side test launcher need to be updated.
