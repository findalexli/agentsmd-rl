#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'export const enableViewTransition: boolean = true;' packages/shared/forks/ReactFeatureFlags.native-fb.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/shared/forks/ReactFeatureFlags.native-fb.js b/packages/shared/forks/ReactFeatureFlags.native-fb.js
index bbb13a6eb174..3f25d8028c98 100644
--- a/packages/shared/forks/ReactFeatureFlags.native-fb.js
+++ b/packages/shared/forks/ReactFeatureFlags.native-fb.js
@@ -68,7 +68,7 @@ export const syncLaneExpirationMs = 250;
 export const transitionLaneExpirationMs = 5000;
 export const enableYieldingBeforePassive: boolean = false;
 export const enableThrottledScheduling: boolean = false;
-export const enableViewTransition: boolean = false;
+export const enableViewTransition: boolean = true;
 export const enableGestureTransition: boolean = false;
 export const enableScrollEndPolyfill: boolean = true;
 export const enableSuspenseyImages: boolean = false;
diff --git a/packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js b/packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js
index 6bc80d2b8e30..a429ef71318a 100644
--- a/packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js
+++ b/packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js
@@ -54,7 +54,7 @@ export const syncLaneExpirationMs = 250;
 export const transitionLaneExpirationMs = 5000;
 export const enableYieldingBeforePassive = false;
 export const enableThrottledScheduling = false;
-export const enableViewTransition = false;
+export const enableViewTransition = true;
 export const enableGestureTransition = false;
 export const enableScrollEndPolyfill = true;
 export const enableSuspenseyImages = false;
diff --git a/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js b/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js
index 85079001ecfe..cebd5b5608d0 100644
--- a/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js
+++ b/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js
@@ -65,7 +65,7 @@ export const enableEffectEventMutationPhase: boolean = false;
 export const enableYieldingBeforePassive: boolean = false;

 export const enableThrottledScheduling: boolean = false;
-export const enableViewTransition: boolean = false;
+export const enableViewTransition: boolean = true;
 export const enableGestureTransition: boolean = false;
 export const enableScrollEndPolyfill: boolean = true;
 export const enableSuspenseyImages = false;

PATCH

echo "Patch applied successfully."
