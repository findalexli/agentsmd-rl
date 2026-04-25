# Fix: Path traversal vulnerability on Windows with Python 3.14

## Problem

A path traversal vulnerability exists in the Gradio codebase that manifests on Windows when running Python 3.14. In Python 3.14, `os.path.isabs` no longer treats paths starting with `/` as absolute on Windows. This means malicious paths like `/etc/passwd`, `/root/.ssh/id_rsa`, and `/var/log/syslog` could bypass the absolute path check and potentially allow unauthorized file access.

## Affected Components

- **File**: `gradio/utils.py`
- **Function**: `safe_join` - validates and joins directory paths with user-provided filenames
- **Helper functions**: `abspath` and `is_in_or_equal` - used for path normalization and containment checks

## Expected Behavior

1. **Path validation**: When `safe_join(directory, filename)` is called, it must reject paths that would allow directory traversal or absolute path access.

2. **Exception type**: When rejecting malicious paths, the function must raise `InvalidPathError` (a ValueError subclass).

3. **Malicious paths that must be rejected** (even when `os.path.isabs` returns False):
   - `/etc/passwd`
   - `/root/.ssh/id_rsa`
   - `/var/log/syslog`
   - `/home/user/.env`
   - `/proc/self/environ`
   - `/etc/shadow`
   - `/opt/secrets/key.pem`
   - `/usr/local/bin/exploit`

4. **Traversal paths that must be rejected**:
   - `..`
   - `../etc/passwd`
   - `../../../root`
   - `../secret.txt`

5. **Valid paths that must be accepted**:
   - `image.png`
   - `subdir/file.txt`
   - `a/b/c/d.txt`
   - `static/style.css`
   - `reports/2024/q1.csv`
   - `file.name.txt` (dots in filenames are OK)

## Code Quality Requirements

- The code must pass ruff lint checks: `ruff check gradio/utils.py`
- The code must pass ruff format checks: `ruff format --check gradio/utils.py`
- The code must have no syntax errors and be compilable
- The `safe_join` function must contain real security logic (not be a stub) with proper validation and exception raising

## Security Context

The `safe_join` function is used to validate user-provided file paths before they are accessed. The function must ensure that:
- Absolute paths are blocked (regardless of platform or Python version behavior)
- Directory traversal attempts using `..` are blocked
- Path containment is properly verified via the `is_in_or_equal` helper function
