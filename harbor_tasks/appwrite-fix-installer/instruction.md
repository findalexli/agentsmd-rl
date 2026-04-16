# Fix Installer — Appwrite #11689

## Background

The Appwrite installer is used for both fresh installations and in-place upgrades of Appwrite. It includes a web-based wizard (`/install`) and a CLI entry point (`appwrite install`). Several bugs have been identified that cause failures in different scenarios.

## Issues to Fix

### 1. Async operations fail silently in the installer server
The installer server starts a Swoole HTTP server to handle concurrent installation steps. When a Swoole server runs without coroutine support enabled, any `Swoole\Coroutine` operations fail silently. This means async tasks within the installer cannot coordinate properly.

**Symptom**: The `startSwooleServer` method in `src/Appwrite/Platform/Installer/Server.php` does not enable coroutines before performing async work. The server needs to enable Swoole's coroutine hooks before any coroutine-based operations are attempted.

**Files**: `src/Appwrite/Platform/Installer/Server.php`

### 2. SSE response hangs when installation completes
When installation finishes via Server-Sent Events (SSE), the frontend waits indefinitely for a `done` event. The tracking telemetry call (`trackSelfHostedInstall`) runs in the same worker thread and blocks it from sending the final SSE event, causing the UI to hang.

**Symptom**: In `src/Appwrite/Platform/Tasks/Install.php`, the `performInstallation` method returns only after the tracking telemetry call completes, even though the SSE response needs to be sent first. The tracking call blocks the worker thread. A mechanism is needed to signal completion to the SSE handler before the (potentially slow) telemetry call runs, so the SSE stream can finish cleanly.

**Files**: `src/Appwrite/Platform/Tasks/Install.php`

### 3. Secret API key shown during upgrades
The installer's step-4 review page displays the "Secret API key" badge even when performing an upgrade. This information is not relevant during upgrades since the key was already set during the initial installation.

**Symptom**: In `app/views/install/installer/templates/steps/step-4.phtml`, the API key badge row always renders, even when `$isUpgrade` is true. This badge should only appear for fresh installations (`$isUpgrade` is false).

**Files**: `app/views/install/installer/templates/steps/step-4.phtml`

### 4. Wrong copy on the final step during upgrades
During upgrades, the installer's final step says "Updating your app…" — this branding is incorrect for Appwrite.

**Symptom**: In `app/views/install/installer/templates/steps/step-5.phtml`, the text "Updating your app" appears instead of the proper Appwrite branding.

**Files**: `app/views/install/installer/templates/steps/step-5.phtml`

### 5. Web installer launches when CLI flags are present
When `--database` or `--http-port` flags are explicitly passed on the CLI, the installer still launches the interactive web installer instead of running non-interactively.

**Symptom**: The `Install.php` task has no way to detect when explicit CLI parameters (arguments starting with `--`) are present. A method is needed to check for explicit CLI params (excluding `--interactive`). When such params are present, the web installer launch should be skipped in favor of non-interactive CLI operation.

**Expected behavior after fix**: `Install.php` should be able to determine whether any explicit `--` arguments were passed (except `--interactive`). When explicit CLI params are detected, the interactive web installer should not be launched.

**Files**: `src/Appwrite/Platform/Tasks/Install.php`

### 6. DNS resolution failure crashes telemetry
When `gethostbyname()` fails (e.g., network is unavailable), it returns `false`. The telemetry code stores this unchanged value and the subsequent check does not catch `false` values, leading to bad data in the telemetry payload.

**Symptom**: In `src/Appwrite/Platform/Tasks/Install.php`, the telemetry collection does not handle `gethostbyname()` returning `false`. When DNS resolution fails, the telemetry key should be `null` rather than `false`, and the suppression operator should be used to prevent warnings.

**Files**: `src/Appwrite/Platform/Tasks/Install.php`

### 7. Upgrade page layout breaks
The upgrade path of the installer page does not have proper CSS constraints for the step container, causing layout issues.

**Symptom**: In `app/views/install/installer/css/styles.css`, the upgrade page container lacks a CSS rule that clears the minimum height constraint. This causes the upgrade page to display incorrectly compared to the install page.

**Files**: `app/views/install/installer/css/styles.css`

### 8. AGENTS.md documentation is outdated
The `AGENTS.md` file contains outdated command references and poor formatting that makes it hard to use as a reference.

**Symptom**: The `AGENTS.md` file does not use a table format for its commands section. A table-based format with columns like "Command" and "Purpose" would improve readability.

**Files**: `AGENTS.md`

## Verification Criteria

After fixes are applied, the following should be true:
1. All PHP files pass syntax check (`php -l`)
2. `Install.php` defines a method to detect explicit CLI parameters (arguments starting with `--`, excluding `--interactive`)
3. `Server.php` enables coroutine hooks via Swoole's Runtime before any async operations
4. `performInstallation` accepts a nullable callable parameter that is called before the tracking telemetry runs
5. `step-4.phtml` hides the API key badge when performing an upgrade
6. `step-5.phtml` contains the correct Appwrite branding text (not "Updating your app")
7. `styles.css` contains a CSS rule for the upgrade page that resets minimum height
8. `AGENTS.md` contains a table-based commands section

Run `composer format` and `composer analyze` to ensure code style compliance.
