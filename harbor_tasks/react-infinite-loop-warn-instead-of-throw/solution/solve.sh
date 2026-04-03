#!/usr/bin/env bash
set -euo pipefail

# Infinite loop detection should warn instead of throw for instrumentation-gated scenarios
# PR #35999

# Check if already applied
if grep -q "nestedUpdateKind" packages/react-reconciler/src/ReactFiberWorkLoop.js; then
    echo "Fix already applied"
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/packages/react-reconciler/src/ReactFiberWorkLoop.js b/packages/react-reconciler/src/ReactFiberWorkLoop.js
index d055b271ad77..15a260bc660c 100644
--- a/packages/react-reconciler/src/ReactFiberWorkLoop.js
+++ b/packages/react-reconciler/src/ReactFiberWorkLoop.js
@@ -751,6 +751,11 @@ let rootWithNestedUpdates: FiberRoot | null = null;
 let isFlushingPassiveEffects = false;
 let didScheduleUpdateDuringPassiveEffects = false;

+const NO_NESTED_UPDATE = 0;
+const NESTED_UPDATE_SYNC_LANE = 1;
+const NESTED_UPDATE_PHASE_SPAWN = 2;
+let nestedUpdateKind: 0 | 1 | 2 = NO_NESTED_UPDATE;
+
 const NESTED_PASSIVE_UPDATE_LIMIT = 50;
 let nestedPassiveUpdateCount: number = 0;
 let rootWithPassiveNestedUpdates: FiberRoot | null = null;
@@ -4313,15 +4318,30 @@ function flushSpawnedWork(): void {
   // hydration lanes in this check, because render triggered by selective
   // hydration is conceptually not an update.
   if (
+    // Was the finished render the result of an update (not hydration)?
+    includesSomeLane(lanes, UpdateLanes) &&
+    // Did it schedule a sync update?
+    includesSomeLane(remainingLanes, SyncUpdateLanes)
+  ) {
+    if (enableProfilerTimer && enableProfilerNestedUpdatePhase) {
+      markNestedUpdateScheduled();
+    }
+
+    // Count the number of times the root synchronously re-renders without
+    // finishing. If there are too many, it indicates an infinite update loop.
+    if (root === rootWithNestedUpdates) {
+      nestedUpdateCount++;
+    } else {
+      nestedUpdateCount = 0;
+      rootWithNestedUpdates = root;
+    }
+    nestedUpdateKind = NESTED_UPDATE_SYNC_LANE;
+  } else if (
     // Check if there was a recursive update spawned by this render, in either
     // the render phase or the commit phase. We track these explicitly because
     // we can't infer from the remaining lanes alone.
-    (enableInfiniteRenderLoopDetection &&
-      (didIncludeRenderPhaseUpdate || didIncludeCommitPhaseUpdate)) ||
-    // Was the finished render the result of an update (not hydration)?
-    (includesSomeLane(lanes, UpdateLanes) &&
-      // Did it schedule a sync update?
-      includesSomeLane(remainingLanes, SyncUpdateLanes))
+    enableInfiniteRenderLoopDetection &&
+    (didIncludeRenderPhaseUpdate || didIncludeCommitPhaseUpdate)
   ) {
     if (enableProfilerTimer && enableProfilerNestedUpdatePhase) {
       markNestedUpdateScheduled();
@@ -4335,8 +4355,11 @@ function flushSpawnedWork(): void {
       nestedUpdateCount = 0;
       rootWithNestedUpdates = root;
     }
+    nestedUpdateKind = NESTED_UPDATE_PHASE_SPAWN;
   } else {
     nestedUpdateCount = 0;
+    rootWithNestedUpdates = null;
+    nestedUpdateKind = NO_NESTED_UPDATE;
   }

   if (enableProfilerTimer && enableComponentPerformanceTrack) {
@@ -5152,25 +5175,47 @@ export function throwIfInfiniteUpdateLoopDetected() {
     rootWithNestedUpdates = null;
     rootWithPassiveNestedUpdates = null;

+    const updateKind = nestedUpdateKind;
+    nestedUpdateKind = NO_NESTED_UPDATE;
+
     if (enableInfiniteRenderLoopDetection) {
-      if (executionContext & RenderContext && workInProgressRoot !== null) {
-        // We're in the render phase. Disable the concurrent error recovery
-        // mechanism to ensure that the error we're about to throw gets handled.
-        // We need it to trigger the nearest error boundary so that the infinite
-        // update loop is broken.
-        workInProgressRoot.errorRecoveryDisabledLanes = mergeLanes(
-          workInProgressRoot.errorRecoveryDisabledLanes,
-          workInProgressRootRenderLanes,
-        );
+      if (updateKind === NESTED_UPDATE_SYNC_LANE) {
+        if (executionContext & RenderContext && workInProgressRoot !== null) {
+          // This loop was identified only because of the instrumentation gated with enableInfiniteRenderLoopDetection, warn instead of throwing.
+          if (__DEV__) {
+            console.error(
+              'Maximum update depth exceeded. This could be an infinite loop. This can happen when a component ' +
+                'repeatedly calls setState during render phase or inside useLayoutEffect, ' +
+                'causing infinite render loop. React limits the number of nested updates to ' +
+                'prevent infinite loops.',
+            );
+          }
+        } else {
+          throw new Error(
+            'Maximum update depth exceeded. This can happen when a component ' +
+              'repeatedly calls setState inside componentWillUpdate or ' +
+              'componentDidUpdate. React limits the number of nested updates to ' +
+              'prevent infinite loops.',
+          );
+        }
+      } else if (updateKind === NESTED_UPDATE_PHASE_SPAWN) {
+        if (__DEV__) {
+          console.error(
+            'Maximum update depth exceeded. This could be an infinite loop. This can happen when a component ' +
+              'repeatedly calls setState during render phase or inside useLayoutEffect, ' +
+              'causing infinite render loop. React limits the number of nested updates to ' +
+              'prevent infinite loops.',
+          );
+        }
       }
+    } else {
+      throw new Error(
+        'Maximum update depth exceeded. This can happen when a component ' +
+          'repeatedly calls setState inside componentWillUpdate or ' +
+          'componentDidUpdate. React limits the number of nested updates to ' +
+          'prevent infinite loops.',
+      );
     }
-
-    throw new Error(
-      'Maximum update depth exceeded. This can happen when a component ' +
-        'repeatedly calls setState inside componentWillUpdate or ' +
-        'componentDidUpdate. React limits the number of nested updates to ' +
-        'prevent infinite loops.',
-    );
   }

   if (__DEV__) {
PATCH

echo "Fix applied successfully"
