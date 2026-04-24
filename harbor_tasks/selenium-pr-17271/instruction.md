# Selenium Manager Platform Detection Issues

The Selenium Manager binary selection logic in `py/selenium/webdriver/common/selenium_manager.py` has several platform detection issues that need to be fixed.

## Problems

1. **Windows ARM64**: The current code allows any architecture on Windows, but the Selenium Manager binary is only available for x86_64. Windows ARM64 users get a confusing generic error instead of a clear unsupported platform message. When this issue occurs, the exception message must contain: `"Unsupported platform/architecture combination"` along with the platform name and architecture.

2. **BSD Platform Names**: On Python versions before 3.14, `sys.platform` returns BSD platform names with version numbers appended (e.g., `freebsd15` instead of `freebsd`). This causes the platform lookup to fail even though a compatible binary exists at `selenium/webdriver/common/linux/selenium-manager`.

3. **Architecture Variants**: Some operating systems report x86-64 architecture as `amd64` or `AMD64` instead of `x86_64`. This inconsistency causes the platform/architecture combination lookup to fail. The binary paths that should work are:
   - `selenium/webdriver/common/windows/selenium-manager.exe` for Windows x86_64
   - `selenium/webdriver/common/linux/selenium-manager` for Linux x86_64
   - `selenium/webdriver/common/linux/selenium-manager` for FreeBSD and OpenBSD x86_64

4. **FreeBSD Warning Message**: The current FreeBSD warning is vague. When a FreeBSD platform is detected (including versions like `freebsd14` or `freebsd15`), the warning should mention either the `brandelf` command or the `linux64.ko` kernel module as actionable guidance for running the Linux binary on FreeBSD.

## Expected Behavior

- Windows with ARM64 architecture should raise a `WebDriverException` with a message containing `"Unsupported platform/architecture combination"`, the platform (e.g., `win32`), and the architecture (e.g., `arm64`)
- FreeBSD and OpenBSD with version numbers in the platform name (e.g., `freebsd15`, `freebsd14`, `openbsd7`) should correctly resolve to the Linux binary at `selenium/webdriver/common/linux/selenium-manager`
- Architecture values like `amd64`, `AMD64`, `x86_64`, and other x86-64 variants should all normalize correctly for the lookup
- The FreeBSD warning message should include actionable guidance mentioning either `brandelf` (e.g., `brandelf -t linux`) or `linux64.ko` (kernel module loading)

## Files to Modify

- `py/selenium/webdriver/common/selenium_manager.py` - The `_get_binary()` method contains the platform detection logic

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
