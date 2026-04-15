# Fix flaky Playwright tests caused by premature server readiness detection

## Problem

Playwright browser tests intermittently fail with errors indicating no content is available on the page. The test infrastructure detects that the Gradio server is "ready" when it sees `Running on local URL:` in the console output, but the server may not actually be ready to handle HTTP requests at that point.

The root cause is in the server readiness checking logic. In `gradio/node_server.py`, the `verify_server_startup()` function uses a raw TCP socket connection to check if the server is up. However, the Node SSR server may accept TCP connections before it's actually ready to serve HTTP responses. This means Gradio's own health check (`url_ok`, which does `HEAD /`) can fail intermittently because the server socket is open but HTTP handling isn't initialized yet.

The same issue exists on the TypeScript side in `js/tootils/src/app-launcher.ts` — the `launchGradioApp()` function resolves its promise as soon as it sees the startup message in stdout, without confirming the server actually responds to HTTP requests.

## Expected Behavior

Both the Python server readiness check and the TypeScript test launcher should verify that the server is actually responding to HTTP requests (not just accepting TCP connections) before declaring the server ready. The readiness check should also handle servers that are accepting connections but returning error responses (5xx).

Specifically:

1. In `gradio/node_server.py`:
   - The `verify_server_startup()` function should use HTTP-based polling (not just TCP socket connection) to verify server readiness
   - The default `timeout` parameter should be at least 10.0 seconds (increased from the original 5.0)
   - It should reject servers that accept TCP connections but don't respond to HTTP requests
   - It should reject servers that return HTTP 5xx error responses
   - It should accept servers that return HTTP 200 responses

2. In `js/tootils/src/app-launcher.ts`:
   - Create a function named `waitForServerReady()` that polls the server with HTTP requests before resolving
   - Import the `http` module (add `import http from "http"` or equivalent) for making HTTP polling requests
   - The `launchGradioApp()` function should use this HTTP polling instead of resolving immediately on stdout messages

## Files to Look At

- `gradio/node_server.py` — contains `verify_server_startup()` which checks if the Node SSR server is ready
- `js/tootils/src/app-launcher.ts` — contains `launchGradioApp()` which starts a Gradio app and waits for it to be ready for Playwright tests
