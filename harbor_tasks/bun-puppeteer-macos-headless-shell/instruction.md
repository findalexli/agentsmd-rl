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

1. **Headless mode on macOS**: The current `headless: true` configuration uses the full Chrome for Testing `.app` bundle on macOS, which is subject to Gatekeeper blocks. On macOS, headless mode must use a non-boolean value that invokes `chrome-headless-shell` (a standalone binary) instead of the full `.app` bundle.

2. **Executable path on macOS**: The code currently passes `executablePath` when a system browser is found, regardless of platform. On macOS with headless shell mode, `executablePath` must be omitted or conditionally excluded, since it points to the full Chrome `.app` bundle rather than `chrome-headless-shell`.

3. **Downloaded binary permissions**: Puppeteer's downloaded browser binaries in the cache may lack execute permissions, contributing to launch failures. Use `chmod` to ensure downloaded binaries (`chrome` and `chrome-headless-shell`) are executable.

4. **Infinite timeouts**: Both `timeout` and `protocolTimeout` are set to `0` (infinite), which can cause tests to hang indefinitely. Both must be set to finite values greater than zero.

5. **Retry delay**: The delay between launch retries is 1000ms, which may be insufficient for transient macOS launch issues. Increase the `setTimeout` delay to more than 1000ms.

## Relevant file

- `test/integration/next-pages/test/dev-server-puppeteer.ts` — Puppeteer browser launch configuration and retry logic

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
