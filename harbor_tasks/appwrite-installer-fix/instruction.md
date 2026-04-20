# Fix Appwrite Installer

The Appwrite installer has several issues that need fixing. Each issue describes a symptom and the expected behavior.

## Issues

### 1. Installer doesn't complete properly in web mode
The web installer uses Server-Sent Events (SSE) to stream progress to the browser. Currently, the SSE response is sent after the tracking operation completes, which can delay the frontend receiving confirmation. The client receives the final event only after all background operations finish.

**Expected behavior:** The `performInstallation` method must accept an optional callable parameter named `onComplete`. The completion callback must be invoked before the tracking call so the SSE stream can finish and the frontend can redirect immediately. A boolean flag named `responseSent` must track whether the response was already sent to prevent duplicate responses.

### 2. Missing Swoole coroutine support
The installer server runs on Swoole but async operations may block the worker thread.

**Expected behavior:** The `Server.php` file must enable Swoole coroutines for non-blocking I/O. The `Swoole\Runtime` class must be imported and `Runtime::enableCoroutine()` must be called with hook flags (e.g., `SWOOLE_HOOK_ALL`) to enable async I/O.

### 3. CLI params don't skip web installer
When running the installer with explicit CLI parameters (like `--database=mysql`), the installer launches the web UI instead of running in CLI mode.

**Expected behavior:** The `Install.php` file must implement a method named `hasExplicitCliParams` that detects when arguments prefixed with `--` (except `--interactive`) are provided, causing the installer to run in CLI mode directly and skip the web installer. The method must use `str_starts_with` for argument detection.

### 4. DNS lookup errors not handled
The tracking code calls `gethostbyname()` without error handling, which can cause warnings or errors if DNS resolution fails.

**Expected behavior:** The `gethostbyname()` call in the tracking code must use the `@` error suppression operator to prevent PHP warnings on DNS failure.

### 5. Tracking payload uses wrong key name for IP address
The tracking payload uses an incorrect key name for the IP address.

**Expected behavior:** The tracking payload in the `trackSelfHostedInstall` function must use the key `'ip'` (not `'hostIp'`) for the IP address field. The code must validate that the DNS lookup succeeded before including the IP — the IP must only be included if `gethostbyname` did not return `false` and the returned IP differs from the domain name (check `!== false` and `!== $domain`).

### 6. HTTP client lacks timeouts
The tracking HTTP client doesn't set timeouts, meaning it can hang indefinitely if the growth API is slow.

**Expected behavior:** The HTTP client must have both connection timeout (`setConnectTimeout`) and request timeout (`setTimeout`) configured with numeric values to prevent hanging on slow networks.

### 7. Existing installation not detected as upgrade
When an existing installation is found but the user runs the installer interactively, the web server doesn't receive the upgrade flag.

**Expected behavior:** When an existing installation is detected, the upgrade flag passed to `startWebServer` must include both the `isUpgrade` variable and the `existingInstallation` variable so the web installer runs in upgrade mode.

### 8. Tracking blocks the worker in Swoole context
The tracking call happens synchronously in the main execution flow, blocking the Swoole worker.

**Expected behavior:** When running in a Swoole context, tracking must run in a non-blocking manner so it doesn't delay other operations. The code must import `Swoole\Coroutine` and detect Swoole context using `Coroutine::getCid()`. When in a Swoole context, tracking must be offloaded to a coroutine using `go(function () { ... })`.

### 9. Step 4 shows secret key during upgrade
The secret key row is shown even when upgrading an existing installation.

**Expected behavior:** The step-4 template (`step-4.phtml`) must conditionally hide the secret API key row based on upgrade mode. The template must check `!$isUpgrade` (or `$isUpgrade === false`) to show the secret key only for fresh installations, not during upgrades.

### 10. Step 5 text uses generic phrasing instead of brand name
The progress text uses "your app" instead of the product name.

**Expected behavior:** The step-5 template (`step-5.phtml`) must say "Installing Appwrite" for fresh installs and "Updating Appwrite" for upgrades. The phrase "your app" must not appear in the template.

### 11. Upgrade mode CSS layout issue
The installer step has incorrect min-height in upgrade mode.

**Expected behavior:** The CSS file must set `min-height: 0` for the `.installer-step` element. The CSS must have an upgrade-specific selector (such as `[data-upgrade='true']` or `.upgrade`) to apply this rule in upgrade mode.

## Guidelines

- The project uses PSR-12 formatting (enforced by Pint)
- PHP 8.3+ with Swoole 6.x
- Utopia PHP framework for HTTP routing
- Always use error suppression or try-catch for external service calls
- Use Swoole coroutines for non-blocking I/O
