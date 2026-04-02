# Bug: Puppeteer browser launch fails intermittently on macOS CI

## Problem

The integration test at `test/integration/next-pages/test/dev-server-puppeteer.ts` intermittently fails on macOS CI with:

```
Browser launch attempt 1/3 failed: Failed to launch the browser process!
Browser launch attempt 2/3 failed: Failed to launch the browser process!
Browser launch attempt 3/3 failed: Failed to launch the browser process!
```

The root cause is that macOS Gatekeeper quarantines the Chrome for Testing `.app` bundle downloaded by Puppeteer, preventing it from launching. The existing `xattr -rd` workaround is not sufficient — the full Chrome `.app` bundle still triggers Gatekeeper in some environments.

Additionally, there are several robustness issues in the current launch configuration:

1. **Headless mode**: The current `headless: true` mode uses the full Chrome for Testing `.app` bundle on macOS, which is subject to Gatekeeper. There is an alternative headless mode that uses a standalone binary not inside a `.app` bundle.

2. **Executable path**: On macOS, when using the alternative headless mode, passing a system browser path is incorrect because it points to full Chrome, not the headless shell binary. The code currently always passes the system browser path when found.

3. **Downloaded binaries may not be executable**: Puppeteer's downloaded browser binaries in the cache may lack execute permissions.

4. **Launch timeouts set to 0**: Both `timeout` and `protocolTimeout` are set to `0` (infinite), which can cause tests to hang indefinitely if the browser fails to respond rather than failing fast.

5. **Retry delay too short**: The 1-second delay between launch retries is insufficient for transient macOS launch issues.

## Relevant file

- `test/integration/next-pages/test/dev-server-puppeteer.ts` — Puppeteer browser launch configuration and retry logic
