# Fix Appwrite Installer

The Appwrite installer has several issues that need fixing.

## Issues

### 1. Installer doesn't complete properly in web mode
The web installer uses Server-Sent Events (SSE) to stream progress to the browser. Currently, the SSE response is sent after the tracking operation completes, which can delay the frontend receiving confirmation. The client receives the final event only after all background operations finish.

The fix must ensure the completion callback is invoked **before** the tracking call so the SSE stream can finish and the frontend can redirect immediately. Additionally, to prevent duplicate responses, a flag must track whether the response was already sent.

### 2. Missing Swoole coroutine support
The installer server runs on Swoole but async operations may block the worker thread. Non-blocking I/O should be enabled for the Swoole server by enabling coroutines at startup.

### 3. CLI params don't skip web installer
When running the installer with explicit CLI parameters (like `--database=mysql`), the installer launches the web UI instead of running in CLI mode. Arguments prefixed with `--` (except `--interactive`) should cause the installer to run in CLI mode directly.

The fix must detect arguments starting with `--` and skip the web installer when any such argument is present (except `--interactive`).

### 4. DNS lookup errors not handled
The tracking code calls `gethostbyname()` without error handling, which can cause warnings or errors if DNS resolution fails. Error suppression must be applied to this call.

### 5. Tracking payload uses wrong key name
The tracking payload uses an incorrect key name for the IP address. The API expects the key to be `'ip'` (not `'hostIp'`). Additionally, the code must validate that the DNS lookup succeeded before including the IP — the IP must only be included if `gethostbyname` did not return `false` and the returned IP differs from the domain name.

### 6. HTTP client lacks timeouts
The tracking HTTP client doesn't set timeouts, meaning it can hang indefinitely if the growth API is slow. Both connection and request timeouts must be configured using `setConnectTimeout` and `setTimeout` methods on the HTTP client.

### 7. Existing installation not detected as upgrade
When an existing installation is found but the user runs the installer interactively, the web server doesn't receive the upgrade flag. Both the existing installation and the upgrade flag should trigger upgrade behavior — the `startWebServer` call must pass `isUpgrade || existingInstallation`.

### 8. Tracking blocks the worker
The tracking call happens synchronously in the main execution flow. When running in a Swoole context, tracking must run in a non-blocking manner so it doesn't delay other operations. The fix must check `Coroutine::getCid()` to detect Swoole context and use `go(function () { ... })` to offload tracking to a coroutine.

### 9. Step 4 shows secret key during upgrade
The secret key row is shown even when upgrading an existing installation. It should only be shown for fresh installations. The fix must wrap the secret key row in a conditional that checks `!$isUpgrade`.

### 10. Step 5 text says "your app" instead of "Appwrite"
The progress text uses "your app" instead of "Appwrite". It must say "Installing Appwrite" for fresh installs and "Updating Appwrite" for upgrades (and must not contain the phrase "your app").

### 11. Upgrade mode CSS issues
The installer step has incorrect min-height in upgrade mode. A CSS rule targeting upgrade mode (`[data-upgrade='true']`) must set `min-height: 0` for the `.installer-step` selector.

## Guidelines

- The project uses PSR-12 formatting (enforced by Pint)
- PHP 8.3+ with Swoole 6.x
- Utopia PHP framework for HTTP routing
- Always use error suppression or try-catch for external service calls
- Use Swoole coroutines for non-blocking I/O
