#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'NESTED_UPDATE_PHASE_SPAWN' packages/react-reconciler/src/ReactFiberWorkLoop.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-dom/src/__tests__/ReactUpdates-test.js b/packages/react-dom/src/__tests__/ReactUpdates-test.js
index 460f77a02f32..cf2e958d4511 100644
--- a/packages/react-dom/src/__tests__/ReactUpdates-test.js
+++ b/packages/react-dom/src/__tests__/ReactUpdates-test.js
@@ -1792,8 +1792,8 @@ describe('ReactUpdates', () => {
     expect(subscribers.length).toBe(limit);
   });

-  it("does not infinite loop if there's a synchronous render phase update on another component", async () => {
-    if (gate(flags => !flags.enableInfiniteRenderLoopDetection)) {
+  it("warns about potential infinite loop if there's a synchronous render phase update on another component", async () => {
+    if (!__DEV__ || gate(flags => !flags.enableInfiniteRenderLoopDetection)) {
       return;
     }
     let setState;
@@ -1809,22 +1809,29 @@ describe('ReactUpdates', () => {
       return null;
     }

-    const container = document.createElement('div');
-    const root = ReactDOMClient.createRoot(container);
-
-    await expect(async () => {
-      await act(() => ReactDOM.flushSync(() => root.render(<App />)));
-    }).rejects.toThrow('Maximum update depth exceeded');
-    assertConsoleErrorDev([
-      'Cannot update a component (`App`) while rendering a different component (`Child`). ' +
-        'To locate the bad setState() call inside `Child`, ' +
-        'follow the stack trace as described in https://react.dev/link/setstate-in-render\n' +
-        '    in App (at **)',
-    ]);
+    const originalConsoleError = console.error;
+    console.error = e => {
+      if (
+        typeof e === 'string' &&
+        e.startsWith(
+          'Maximum update depth exceeded. This could be an infinite loop.',
+        )
+      ) {
+        Scheduler.log('stop');
+      }
+    };
+    try {
+      const container = document.createElement('div');
+      const root = ReactDOMClient.createRoot(container);
+      root.render(<App />);
+      await waitFor(['stop']);
+    } finally {
+      console.error = originalConsoleError;
+    }
   });

-  it("does not infinite loop if there's an async render phase update on another component", async () => {
-    if (gate(flags => !flags.enableInfiniteRenderLoopDetection)) {
+  it("warns about potential infinite loop if there's an async render phase update on another component", async () => {
+    if (!__DEV__ || gate(flags => !flags.enableInfiniteRenderLoopDetection)) {
       return;
     }
     let setState;
@@ -1840,21 +1847,25 @@ describe('ReactUpdates', () => {
       return null;
     }

-    const container = document.createElement('div');
-    const root = ReactDOMClient.createRoot(container);
-
-    await expect(async () => {
-      await act(() => {
-        React.startTransition(() => root.render(<App />));
-      });
-    }).rejects.toThrow('Maximum update depth exceeded');
-
-    assertConsoleErrorDev([
-      'Cannot update a component (`App`) while rendering a different component (`Child`). ' +
-        'To locate the bad setState() call inside `Child`, ' +
-        'follow the stack trace as described in https://react.dev/link/setstate-in-render\n' +
-        '    in App (at **)',
-    ]);
+    const originalConsoleError = console.error;
+    console.error = e => {
+      if (
+        typeof e === 'string' &&
+        e.startsWith(
+          'Maximum update depth exceeded. This could be an infinite loop.',
+        )
+      ) {
+        Scheduler.log('stop');
+      }
+    };
+    try {
+      const container = document.createElement('div');
+      const root = ReactDOMClient.createRoot(container);
+      React.startTransition(() => root.render(<App />));
+      await waitFor(['stop']);
+    } finally {
+      console.error = originalConsoleError;
+    }
   });

   // TODO: Replace this branch with @gate pragmas
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

echo "Patch applied successfully."
