#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Check if already applied (idempotency check)
if grep -q "enableTrustedTypesIntegration: boolean = __VARIANT__" packages/shared/forks/ReactFeatureFlags.www-dynamic.js 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the fix: make enableTrustedTypesIntegration a dynamic __VARIANT__ flag
git apply - <<'PATCH'
diff --git a/packages/shared/forks/ReactFeatureFlags.www-dynamic.js b/packages/shared/forks/ReactFeatureFlags.www-dynamic.js
index a8d829ee3e31..3a6c456c928f 100644
--- a/packages/shared/forks/ReactFeatureFlags.www-dynamic.js
+++ b/packages/shared/forks/ReactFeatureFlags.www-dynamic.js
@@ -35,12 +35,11 @@ export const enableScrollEndPolyfill: boolean = __VARIANT__;
 export const enableFragmentRefs: boolean = __VARIANT__;
 export const enableFragmentRefsScrollIntoView: boolean = __VARIANT__;
 export const enableAsyncDebugInfo: boolean = __VARIANT__;
-
 export const enableInternalInstanceMap: boolean = __VARIANT__;
+export const enableTrustedTypesIntegration: boolean = __VARIANT__;

 // TODO: These flags are hard-coded to the default values used in open source.
 // Update the tests so that they pass in either mode, then set these
 // to __VARIANT__.
-export const enableTrustedTypesIntegration: boolean = false;
 // You probably *don't* want to add more hardcoded ones.
 // Instead, try to add them above with the __VARIANT__ value.
 PATCH

echo "Patch applied successfully"
