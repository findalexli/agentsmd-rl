#!/usr/bin/env bash
set -euo pipefail

cd /workspace/httpjail

# Idempotency guard
if grep -qF "The integration tests run against the binary built by Cargo; no manual environme" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -31,12 +31,22 @@ variables to the proxy address.
 
 ### Integration Tests
 
-The integration tests use the `HTTPJAIL_BIN` environment variable to determine which binary to test.
-Always set this to the most up-to-date binary before running tests:
+The integration tests run against the binary built by Cargo; no manual environment variables are required. On Linux, run the strong-jail integration tests with sudo:
 
 ```bash
-export HTTPJAIL_BIN=/path/to/httpjail
-cargo test --test linux_integration
+sudo -E cargo test --test linux_integration
+```
+
+Weak-mode tests (environment-only, cross-platform) run without sudo:
+
+```bash
+cargo test --test weak_integration
+```
+
+Run the full suite:
+
+```bash
+cargo test
 ```
 
 ## Cargo Cache
@@ -46,9 +56,11 @@ DO NOT `cargo clean`. Instead, `chown -R <user> target`.
 
 ## macOS
 
-- On macOS, use `SUDO_ASKPASS=$(pwd)/askpass_macos.sh sudo -A <cmd>` to test jail features with sufficient permissions.
-- To debug pf, you may run the command with `--no-jail-cleanup` to leave around the `httpjail` group
-  and PF rules.
+- macOS uses weak mode (environment-only) and does not use PF. No root/sudo required for standard usage or tests.
+- To run integration tests on macOS, prefer the weak-mode suite:
+  ```bash
+  cargo test --test weak_integration
+  ```
 
 ## Documentation
 
PATCH

echo "Gold patch applied."
