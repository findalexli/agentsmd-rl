#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if already applied (idempotency check)
if grep -q "enableFragmentRefsInstanceHandles: boolean = true;" packages/shared/ReactFeatureFlags.js; then
    echo "Fix already applied, skipping..."
    exit 0
fi

echo "Applying feature flag changes..."

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/packages/shared/ReactFeatureFlags.js b/packages/shared/ReactFeatureFlags.js
index ee5f22ab9588..a54483df456e 100644
--- a/packages/shared/ReactFeatureFlags.js
+++ b/packages/shared/ReactFeatureFlags.js
@@ -145,7 +145,7 @@ export const enableInfiniteRenderLoopDetection: boolean = false;

 export const enableFragmentRefs: boolean = true;
 export const enableFragmentRefsScrollIntoView: boolean = true;
-export const enableFragmentRefsInstanceHandles: boolean = false;
+export const enableFragmentRefsInstanceHandles: boolean = true;
 export const enableFragmentRefsTextNodes: boolean = true;

 export const enableInternalInstanceMap: boolean = false;
diff --git a/packages/shared/forks/ReactFeatureFlags.native-oss.js b/packages/shared/forks/ReactFeatureFlags.native-oss.js
index 6b0d93447966..1c34990f5814 100644
--- a/packages/shared/forks/ReactFeatureFlags.native-oss.js
+++ b/packages/shared/forks/ReactFeatureFlags.native-oss.js
@@ -70,8 +70,8 @@ export const ownerStackLimit = 1e4;

 export const enableFragmentRefs: boolean = true;
 export const enableFragmentRefsScrollIntoView: boolean = false;
-export const enableFragmentRefsInstanceHandles: boolean = false;
-export const enableFragmentRefsTextNodes: boolean = false;
+export const enableFragmentRefsInstanceHandles: boolean = true;
+export const enableFragmentRefsTextNodes: boolean = true;

 export const enableInternalInstanceMap: boolean = false;

diff --git a/packages/shared/forks/ReactFeatureFlags.test-renderer.js b/packages/shared/forks/ReactFeatureFlags.test-renderer.js
index 954d9d88eaf5..40b6926c3572 100644
--- a/packages/shared/forks/ReactFeatureFlags.test-renderer.js
+++ b/packages/shared/forks/ReactFeatureFlags.test-renderer.js
@@ -71,7 +71,7 @@ export const ownerStackLimit = 1e4;

 export const enableFragmentRefs: boolean = true;
 export const enableFragmentRefsScrollIntoView: boolean = true;
-export const enableFragmentRefsInstanceHandles: boolean = false;
+export const enableFragmentRefsInstanceHandles: boolean = true;
 export const enableFragmentRefsTextNodes: boolean = true;

 export const enableInternalInstanceMap: boolean = false;
diff --git a/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js b/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js
index 91dc33b28f35..85079001ecfe 100644
--- a/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js
+++ b/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js
@@ -74,10 +74,10 @@ export const enableSrcObject: boolean = false;
 export const enableHydrationChangeEvent: boolean = false;
 export const enableDefaultTransitionIndicator: boolean = true;

-export const enableFragmentRefs: boolean = false;
-export const enableFragmentRefsScrollIntoView: boolean = false;
-export const enableFragmentRefsInstanceHandles: boolean = false;
-export const enableFragmentRefsTextNodes: boolean = false;
+export const enableFragmentRefs: boolean = true;
+export const enableFragmentRefsScrollIntoView: boolean = true;
+export const enableFragmentRefsInstanceHandles: boolean = true;
+export const enableFragmentRefsTextNodes: boolean = true;
 export const ownerStackLimit = 1e4;

 export const enableInternalInstanceMap: boolean = false;
PATCH

echo "Feature flag changes applied successfully."
