#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if already applied
if grep -q "enableTrustedTypesIntegration: boolean = true" packages/shared/ReactFeatureFlags.js 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the patch to enable Trusted Types integration
git apply - <<'PATCH'
diff --git a/packages/shared/ReactFeatureFlags.js b/packages/shared/ReactFeatureFlags.js
index be13ab9e5dea..7eb81cc72200 100644
--- a/packages/shared/ReactFeatureFlags.js
+++ b/packages/shared/ReactFeatureFlags.js
@@ -208,7 +208,7 @@ export const disableLegacyMode: boolean = true;
 // in open source, but www codebase still relies on it. Need to remove.
 export const disableCommentsAsDOMContainers: boolean = true;

-export const enableTrustedTypesIntegration: boolean = false;
+export const enableTrustedTypesIntegration: boolean = true;

 // Prevent the value and checked attributes from syncing with their related
 // DOM properties
diff --git a/packages/shared/forks/ReactFeatureFlags.native-fb.js b/packages/shared/forks/ReactFeatureFlags.native-fb.js
index a587e425703b..cb994a6d94ed 100644
--- a/packages/shared/forks/ReactFeatureFlags.native-fb.js
+++ b/packages/shared/forks/ReactFeatureFlags.native-fb.js
@@ -62,7 +62,7 @@ export const enableSuspenseAvoidThisFallback: boolean = false;
 export const enableSuspenseCallback: boolean = true;
 export const enableTaint: boolean = true;
 export const enableTransitionTracing: boolean = false;
-export const enableTrustedTypesIntegration: boolean = false;
+export const enableTrustedTypesIntegration: boolean = true;
 export const enableUpdaterTracking: boolean = __PROFILE__;
 export const retryLaneExpirationMs = 5000;
 export const syncLaneExpirationMs = 250;
diff --git a/packages/shared/forks/ReactFeatureFlags.native-oss.js b/packages/shared/forks/ReactFeatureFlags.native-oss.js
index 72904e251cae..69e9f8138962 100644
--- a/packages/shared/forks/ReactFeatureFlags.native-oss.js
+++ b/packages/shared/forks/ReactFeatureFlags.native-oss.js
@@ -50,7 +50,7 @@ export const enableSuspenseAvoidThisFallback: boolean = false;
 export const enableSuspenseCallback: boolean = false;
 export const enableTaint: boolean = true;
 export const enableTransitionTracing: boolean = false;
-export const enableTrustedTypesIntegration: boolean = false;
+export const enableTrustedTypesIntegration: boolean = true;
 export const passChildrenWhenCloningPersistedNodes: boolean = false;
 export const retryLaneExpirationMs = 5000;
 export const syncLaneExpirationMs = 250;
diff --git a/packages/shared/forks/ReactFeatureFlags.test-renderer.js b/packages/shared/forks/ReactFeatureFlags.test-renderer.js
index afa71d5754c6..3dbfe18b07a3 100644
--- a/packages/shared/forks/ReactFeatureFlags.test-renderer.js
+++ b/packages/shared/forks/ReactFeatureFlags.test-renderer.js
@@ -26,7 +26,7 @@ export const disableInputAttributeSyncing: boolean = false;
 export const enableScopeAPI: boolean = false;
 export const enableCreateEventHandleAPI: boolean = false;
 export const enableSuspenseCallback: boolean = false;
-export const enableTrustedTypesIntegration: boolean = false;
+export const enableTrustedTypesIntegration: boolean = true;
 export const disableTextareaChildren: boolean = false;
 export const enableSuspenseAvoidThisFallback: boolean = false;
 export const enableCPUSuspense: boolean = false;
diff --git a/packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js b/packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js
index a81f67ee94fe..79aeed5c24a1 100644
--- a/packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js
+++ b/packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js
@@ -47,7 +47,7 @@ export const enableSuspenseAvoidThisFallback = false;
 export const enableSuspenseCallback = false;
 export const enableTaint = true;
 export const enableTransitionTracing = false;
-export const enableTrustedTypesIntegration = false;
+export const enableTrustedTypesIntegration = true;
 export const enableUpdaterTracking = false;
 export const passChildrenWhenCloningPersistedNodes = false;
 export const retryLaneExpirationMs = 5000;
diff --git a/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js b/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js
index d819bd275eb5..cc870fe329bf 100644
--- a/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js
+++ b/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js
@@ -28,7 +28,7 @@ export const enableCreateEventHandleAPI: boolean = false;
 export const enableSuspenseCallback: boolean = true;
 export const disableLegacyContext: boolean = false;
 export const disableLegacyContextForFunctionComponents: boolean = false;
-export const enableTrustedTypesIntegration: boolean = false;
+export const enableTrustedTypesIntegration: boolean = true;
 export const disableTextareaChildren: boolean = false;
 export const enableSuspenseAvoidThisFallback: boolean = true;
 export const enableCPUSuspense: boolean = false;
diff --git a/packages/shared/forks/ReactFeatureFlags.www-dynamic.js b/packages/shared/forks/ReactFeatureFlags.www-dynamic.js
index ea0751e87dac..496b9c701143 100644
--- a/packages/shared/forks/ReactFeatureFlags.www-dynamic.js
+++ b/packages/shared/forks/ReactFeatureFlags.www-dynamic.js
@@ -36,7 +36,6 @@ export const enableFragmentRefs: boolean = __VARIANT__;
 export const enableFragmentRefsScrollIntoView: boolean = __VARIANT__;
 export const enableFragmentRefsTextNodes: boolean = __VARIANT__;
 export const enableInternalInstanceMap: boolean = __VARIANT__;
-export const enableTrustedTypesIntegration: boolean = __VARIANT__;
 export const enableParallelTransitions: boolean = __VARIANT__;

 export const enableEffectEventMutationPhase: boolean = __VARIANT__;
diff --git a/packages/shared/forks/ReactFeatureFlags.www.js b/packages/shared/forks/ReactFeatureFlags.www.js
index 0c8ec7f25aa4..2a2b7cbfa489 100644
--- a/packages/shared/forks/ReactFeatureFlags.www.js
+++ b/packages/shared/forks/ReactFeatureFlags.www.js
@@ -25,7 +25,6 @@ export const {
   enableObjectFiber,
   enableRetryLaneExpiration,
   enableTransitionTracing,
-  enableTrustedTypesIntegration,
   retryLaneExpirationMs,
   syncLaneExpirationMs,
   transitionLaneExpirationMs,
@@ -45,7 +44,7 @@ export const enableProfilerTimer = __PROFILE__;
 export const enableProfilerCommitHooks = __PROFILE__;
 export const enableProfilerNestedUpdatePhase = __PROFILE__;
 export const enableUpdaterTracking = __PROFILE__;
-
+export const enableTrustedTypesIntegration: boolean = true;
 export const enableSuspenseAvoidThisFallback: boolean = true;

 export const enableAsyncDebugInfo: boolean = true;
PATCH

echo "Patch applied successfully"
