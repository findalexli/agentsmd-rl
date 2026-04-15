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

1. **Headless mode**: The current `headless: true` mode uses the full Chrome for Testing `.app` bundle on macOS, which is subject to Gatekeeper blocks. The headless mode should be made platform-aware so that macOS avoids the `.app` bundle entirely, while Linux keeps the current behavior.

2. **Executable path**: The code currently always passes `executablePath` when a system browser is found, regardless of platform. This behavior should be re-evaluated for correctness on macOS, considering the headless mode selection.

3. **Downloaded binary permissions**: Puppeteer's downloaded browser binaries in the cache may lack execute permissions, contributing to launch failures.

4. **Infinite timeouts**: Both `timeout` and `protocolTimeout` are set to `0` (infinite), which can cause tests to hang indefinitely when the browser fails to respond rather than failing fast.

5. **Retry delay**: The delay between launch retries is only 1 second, which is insufficient for transient macOS launch issues to resolve before the next attempt.

## Relevant file

- `test/integration/next-pages/test/dev-server-puppeteer.ts` — Puppeteer browser launch configuration and retry logic
