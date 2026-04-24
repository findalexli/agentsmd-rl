# Fix Appwrite Installer

The Appwrite installer has several issues that need fixing. Each issue describes a symptom and the expected behavior.

## Issues

### 1. Installer doesn't complete properly in web mode
The web installer uses Server-Sent Events (SSE) to stream progress to the browser. Currently, the SSE response is sent after the tracking operation completes, which can delay the frontend receiving confirmation. The client receives the final event only after all background operations finish.

**Expected behavior:** The installation completion signal must be sent before the tracking call so the SSE stream can finish and the frontend can redirect immediately. The system must prevent duplicate completion signals from being sent.

### 2. Missing async runtime support
The installer server runs on Swoole but async operations may block the worker thread. The server must enable the async runtime so that non-blocking I/O works correctly.

**Expected behavior:** The server must import and enable the async runtime when starting the Swoole server.

### 3. CLI params don't skip web installer
When running the installer with explicit CLI parameters (like `--database=mysql`), the installer launches the web UI instead of running in CLI mode.

**Expected behavior:** The installer must detect when explicit CLI parameters are provided (arguments prefixed with `--`, excluding `--interactive`) and skip the web installer in that case. This detection must use `$_SERVER['argv']` and a string-prefix check function to identify CLI arguments.

### 4. DNS lookup errors not handled
The tracking code calls DNS lookup without error handling, which can cause PHP warnings or errors if DNS resolution fails.

**Expected behavior:** DNS lookups must use error suppression (the `@` operator) to prevent warnings on failure.

### 5. Tracking payload uses wrong key name for IP address
The tracking payload uses an incorrect key name for the IP address field, causing analytics to not capture the IP correctly.

**Expected behavior:** The tracking payload must use the key `'ip'` (not `'hostIp'`) for the IP address field. The code must also validate that the DNS lookup result is valid (not `false`) and differs from the domain name before including it in the payload.

### 6. HTTP client lacks timeouts
The tracking HTTP client doesn't set timeouts, meaning it can hang indefinitely if the growth API is slow.

**Expected behavior:** The HTTP client must set both a connection timeout and a request timeout with numeric values to prevent hanging on slow networks. The client must use `setConnectTimeout()` and `setTimeout()` methods on the HTTP client instance.

### 7. Existing installation not detected as upgrade
When an existing installation is found but the user runs the installer interactively, the web server doesn't receive the upgrade flag.

**Expected behavior:** When an existing installation is detected, the upgrade flag passed to the web server must include the existing installation status (the `isUpgrade` variable must be set to `true` when either the upgrade flag is set OR an existing installation is detected).

### 8. Tracking blocks the worker in Swoole context
The tracking call happens synchronously in the main execution flow, blocking the Swoole worker.

**Expected behavior:** When running in a Swoole context, tracking must run in a non-blocking manner so it doesn't delay other operations. The code must use `Coroutine::getCid()` to detect Swoole context and use `go()` to run the tracking in a coroutine.

### 9. Step 4 shows secret key during upgrade
The secret key row is shown even when upgrading an existing installation.

**Expected behavior:** The step-4 template (`step-4.phtml`) must conditionally hide the secret API key row when in upgrade mode (using a check against `$isUpgrade`).

### 10. Step 5 text uses generic phrasing instead of brand name
The progress text uses "your app" instead of the product name.

**Expected behavior:** The step-5 template (`step-5.phtml`) must say "Installing Appwrite" for fresh installs and "Updating Appwrite" for upgrades. The phrase "your app" must not appear in the template.

### 11. Upgrade mode CSS layout issue
The installer step has incorrect min-height in upgrade mode.

**Expected behavior:** The CSS file (`styles.css`) must set `min-height: 0` for the installer step when a `[data-upgrade='true']` selector is active.

## Files to modify

- `src/Appwrite/Platform/Installer/Server.php` — async runtime enable
- `src/Appwrite/Platform/Installer/Http/Installer/Install.php` — completion callback mechanism
- `src/Appwrite/Platform/Tasks/Install.php` — CLI detection, DNS handling, tracking, timeouts
- `app/views/install/installer/templates/steps/step-4.phtml` — secret key conditional
- `app/views/install/installer/templates/steps/step-5.phtml` — brand name text
- `app/views/install/installer/css/styles.css` — upgrade min-height

## Guidelines

- The project uses PSR-12 formatting (enforced by Pint)
- PHP 8.3+ with Swoole 6.x
- Utopia PHP framework for HTTP routing
- Always use error suppression or try-catch for external service calls
- Use non-blocking patterns for async I/O when in Swoole context