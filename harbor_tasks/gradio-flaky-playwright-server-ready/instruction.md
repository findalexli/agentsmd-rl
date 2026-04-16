# Fix flaky Playwright tests caused by premature server readiness detection

## Problem

Playwright browser tests intermittently fail with errors indicating no content is available on the page. The test infrastructure detects that the Gradio server is "ready" when it sees `Running on local URL:` in the console output, but the server may not actually be ready to handle HTTP requests at that point.

The root cause is in the server readiness checking logic. The current implementation uses a raw TCP socket connection to check if the server is up. However, the Node SSR server may accept TCP connections before it's actually ready to serve HTTP responses. This means Gradio's own health check (`url_ok`, which does `HEAD /`) can fail intermittently because the server socket is open but HTTP handling isn't initialized yet.

The same issue exists on the TypeScript side — the test launcher resolves its promise as soon as it sees the startup message in stdout, without confirming the server actually responds to HTTP requests.

## Expected Behavior

Both the Python server readiness check and the TypeScript test launcher should verify that the server is actually responding to HTTP requests (not just accepting TCP connections) before declaring the server ready. The readiness check should also handle servers that are accepting connections but returning error responses (HTTP 5xx).

Specifically:

1. The Python readiness check should:
   - Use HTTP-based polling (not just TCP socket connection) to verify server readiness
   - Have a default timeout of at least 10.0 seconds (increased from the original 5.0 seconds)
   - Return `False` for servers that accept TCP connections but don't respond to HTTP requests
   - Return `False` for servers that return HTTP 5xx error responses
   - Return `True` for servers that return HTTP 200 responses

2. The TypeScript test launcher should:
   - Poll the server with HTTP requests before resolving (instead of resolving immediately on stdout messages)
   - Import the Node.js `http` module for making HTTP polling requests
   - Use an appropriate polling interval and timeout to ensure the server is truly ready
