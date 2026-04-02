#!/bin/bash
set -euo pipefail

# Check if already applied
if grep -q "^export const enableComponentPerformanceTrack: boolean = true;" packages/shared/forks/ReactFeatureFlags.native-fb.js 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

cd /workspace/react

# Apply the patch to make enableComponentPerformanceTrack static everywhere
git apply - <<'PATCH'
diff --git a/packages/shared/forks/ReactFeatureFlags.native-fb-dynamic.js b/packages/shared/forks/ReactFeatureFlags.native-fb-dynamic.js
index c1d8ea3ceaae..fe7777eda713 100644
--- a/packages/shared/forks/ReactFeatureFlags.native-fb-dynamic.js
+++ b/packages/shared/forks/ReactFeatureFlags.native-fb-dynamic.js
@@ -25,4 +25,3 @@ export const passChildrenWhenCloningPersistedNodes = __VARIANT__;
 export const enableFragmentRefs = __VARIANT__;
 export const enableFragmentRefsScrollIntoView = __VARIANT__;
 export const enableFragmentRefsInstanceHandles = __VARIANT__;
-export const enableComponentPerformanceTrack = __VARIANT__;
diff --git a/packages/shared/forks/ReactFeatureFlags.native-fb.js b/packages/shared/forks/ReactFeatureFlags.native-fb.js
index dab30e7f115c..d516581486e7 100644
--- a/packages/shared/forks/ReactFeatureFlags.native-fb.js
+++ b/packages/shared/forks/ReactFeatureFlags.native-fb.js
@@ -77,8 +77,7 @@ export const enableSrcObject: boolean = false;
 export const enableHydrationChangeEvent: boolean = true;
 export const enableDefaultTransitionIndicator: boolean = true;
 export const ownerStackLimit = 1e4;
-export const enableComponentPerformanceTrack: boolean =
-  __PROFILE__ && dynamicFlags.enableComponentPerformanceTrack;
+export const enableComponentPerformanceTrack: boolean = true;
 export const enablePerformanceIssueReporting: boolean =
   enableComponentPerformanceTrack;
 export const enableInternalInstanceMap: boolean = false;
diff --git a/packages/shared/forks/ReactFeatureFlags.www-dynamic.js b/packages/shared/forks/ReactFeatureFlags.www-dynamic.js
index c5a0cf63fd6c..8a829ee3e31 100644
--- a/packages/shared/forks/ReactFeatureFlags.www-dynamic.js
+++ b/packages/shared/forks/ReactFeatureFlags.www-dynamic.js
@@ -31,7 +31,6 @@ export const enableInfiniteRenderLoopDetection: boolean = __VARIANT__;

 export const enableFastAddPropertiesInDiffing: boolean = __VARIANT__;
 export const enableViewTransition: boolean = __VARIANT__;
-export const enableComponentPerformanceTrack: boolean = __VARIANT__;
 export const enableScrollEndPolyfill: boolean = __VARIANT__;
 export const enableFragmentRefs: boolean = __VARIANT__;
 export const enableFragmentRefsScrollIntoView: boolean = __VARIANT__;
diff --git a/packages/shared/forks/ReactFeatureFlags.www.js b/packages/shared/forks/ReactFeatureFlags.www.js
index bc64b65053bd..8a710cc429d6 100644
--- a/packages/shared/forks/ReactFeatureFlags.www.js
+++ b/packages/shared/forks/ReactFeatureFlags.www.js
@@ -29,7 +29,6 @@ export const {
   syncLaneExpirationMs,
   transitionLaneExpirationMs,
   enableViewTransition,
-  enableComponentPerformanceTrack,
   enableScrollEndPolyfill,
   enableFragmentRefs,
   enableFragmentRefsScrollIntoView,
@@ -56,6 +55,8 @@ export const enableYieldingBeforePassive: boolean = false;

 export const enableThrottledScheduling: boolean = false;

+export const enableComponentPerformanceTrack: boolean = true;
+
 export const enablePerformanceIssueReporting: boolean = false;

 // Logs additional User Timing API marks for use with an experimental profiling tool.
PATCH

echo "Patch applied successfully"
