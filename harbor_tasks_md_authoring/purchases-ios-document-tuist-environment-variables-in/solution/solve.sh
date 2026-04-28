#!/usr/bin/env bash
set -euo pipefail

cd /workspace/purchases-ios

# Idempotency guard
if grep -qF "| `TUIST_LAUNCH_ARGUMENTS=\"-Flag1 -Flag2\"` | Space-separated launch arguments in" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -139,6 +139,24 @@ For environment setup, see **`Contributing/CONTRIBUTING.md`**. For code style, s
 
 The project uses **Tuist** for managing the Xcode workspace. See **`Contributing/DEVELOPMENT.md`** for full Tuist commands, environment variables, and troubleshooting.
 
+**Tuist environment variables** (prefix all with `TUIST_` when passing to `tuist generate`):
+
+| Variable | Purpose | Default |
+|----------|---------|---------|
+| `TUIST_RC_REMOTE=true` | Use remote instead of local RevenueCat dependency | local |
+| `TUIST_RC_XCODE_PROJECT=true` | Use Xcode project instead of Swift Package dependency | SPM |
+| `TUIST_INCLUDE_TEST_DEPENDENCIES=false` | Skip test/dev dependencies (Nimble, OHHTTPStubs, etc.) to speed up `tuist install` | `true` |
+| `TUIST_INCLUDE_XCFRAMEWORK_INSTALLATION_TESTS=true` | Include XCFrameworkInstallationTests project | `false` |
+| `TUIST_SK_CONFIG_PATH=/path/to/file.storekit` | Custom StoreKit config for PaywallsTester scheme | — |
+| `TUIST_RC_API_KEY=appl_xxxxx` | RevenueCat API key written to `Local.xcconfig` at generation time | — |
+| `TUIST_LAUNCH_ARGUMENTS="-Flag1 -Flag2"` | Space-separated launch arguments injected into PaywallsTester scheme run action (enabled by default) | — |
+| `TUIST_SWIFT_CONDITIONS="FLAG1 FLAG2"` | Space-separated Swift compilation conditions injected into all targets | — |
+
+Example combining multiple variables:
+```bash
+TUIST_RC_API_KEY=appl_xxxxx TUIST_LAUNCH_ARGUMENTS="-EnableWorkflowsEndpoint" tuist generate PaywallsTester
+```
+
 ### Target Specifications
 - **Minimum Deployment**: iOS 13.0, macOS 10.15, tvOS 13.0, watchOS 6.2, visionOS 1.0
 - **Swift**: 5.9+
PATCH

echo "Gold patch applied."
