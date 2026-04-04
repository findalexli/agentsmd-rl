#!/bin/bash
set -euo pipefail

# Apply the fix for false-positive re-render reports in DevTools

REPO_DIR="${1:-/workspace/react}"
FILE_PATH="$REPO_DIR/packages/react-devtools-shared/src/backend/fiber/renderer.js"

# Check if already applied (look for the prevFiber !== fiber check)
if grep -q 'prevFiber !== fiber && didFiberRender' "$FILE_PATH"; then
    echo "Fix already applied."
    exit 0
fi

echo "Applying fix for false-positive re-render reports..."

cd "$REPO_DIR"

git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/__tests__/profilingCharts-test.js b/packages/react-devtools-shared/src/__tests__/profilingCharts-test.js
index e54af61d6209..da20511a650e 100644
--- a/packages/react-devtools-shared/src/__tests__/profilingCharts-test.js
+++ b/packages/react-devtools-shared/src/__tests__/profilingCharts-test.js
@@ -298,4 +298,164 @@ describe('profiling charts', () => {
       `);
     });
   });
+
+  describe('components behind filtered fibers should not report false re-renders', () => {
+    it('should not report a component as re-rendered when its filtered parent bailed out', () => {
+      let triggerUpdate;
+
+      function Count() {
+        const [count, setCount] = React.useState(0);
+        triggerUpdate = () => setCount(c => c + 1);
+        Scheduler.unstable_advanceTime(5);
+        return count;
+      }
+
+      function Greeting() {
+        Scheduler.unstable_advanceTime(3);
+        return 'Hello';
+      }
+
+      function App() {
+        Scheduler.unstable_advanceTime(1);
+        return (
+          <React.Fragment>
+            <Count />
+            <div>
+              <Greeting />
+            </div>
+          </React.Fragment>
+        );
+      }
+
+      utils.act(() => store.profilerStore.startProfiling());
+      utils.act(() => render(<App />));
+
+      // Verify tree structure: div is filtered, so Greeting appears as child of App
+      expect(store).toMatchInlineSnapshot(`
+        [root]
+          ▾ <App>
+              <Count>
+              <Greeting>
+      `);
+
+      // Trigger a state update in Count. Should not cause Greeting to re-render.
+      utils.act(() => triggerUpdate());
+
+      utils.act(() => store.profilerStore.stopProfiling());
+
+      const rootID = store.roots[0];
+      const {chartData} = getFlamegraphChartData(rootID, 1);
+      const allNodes = chartData.rows.flat();
+
+      expect(allNodes).toEqual([
+        expect.objectContaining({name: 'App', didRender: false}),
+        expect.objectContaining({name: 'Greeting', didRender: false}),
+        expect.objectContaining({name: 'Count', didRender: true}),
+      ]);
+    });
+
+    it('should not report a component as re-rendered when behind a filtered fragment', () => {
+      let triggerUpdate;
+
+      function Count() {
+        const [count, setCount] = React.useState(0);
+        triggerUpdate = () => setCount(c => c + 1);
+        Scheduler.unstable_advanceTime(5);
+        return count;
+      }
+
+      function Greeting() {
+        Scheduler.unstable_advanceTime(3);
+        return 'Hello';
+      }
+
+      function App() {
+        Scheduler.unstable_advanceTime(1);
+        return (
+          <React.Fragment>
+            <Count />
+            <React.Fragment>
+              <Greeting />
+            </React.Fragment>
+          </React.Fragment>
+        );
+      }
+
+      utils.act(() => store.profilerStore.startProfiling());
+      utils.act(() => render(<App />));
+
+      // Fragment with null key is filtered, so Greeting appears as child of App
+      expect(store).toMatchInlineSnapshot(`
+        [root]
+          ▾ <App>
+              <Count>
+              <Greeting>
+      `);
+
+      // Trigger a state update in Count
+      utils.act(() => triggerUpdate());
+
+      utils.act(() => store.profilerStore.stopProfiling());
+
+      const rootID = store.roots[0];
+      const {chartData} = getFlamegraphChartData(rootID, 1);
+      const allNodes = chartData.rows.flat();
+
+      expect(allNodes).toEqual([
+        expect.objectContaining({name: 'App', didRender: false}),
+        expect.objectContaining({name: 'Greeting', didRender: false}),
+        expect.objectContaining({name: 'Count', didRender: true}),
+      ]);
+    });
+
+    it('should correctly report sibling components that did not re-render', () => {
+      let triggerUpdate;
+
+      function Count() {
+        const [count, setCount] = React.useState(0);
+        triggerUpdate = () => setCount(c => c + 1);
+        Scheduler.unstable_advanceTime(5);
+        return count;
+      }
+
+      function Greeting() {
+        Scheduler.unstable_advanceTime(3);
+        return 'Hello';
+      }
+
+      function App() {
+        Scheduler.unstable_advanceTime(1);
+        return (
+          <React.Fragment>
+            <Count />
+            <Greeting />
+          </React.Fragment>
+        );
+      }
+
+      utils.act(() => store.profilerStore.startProfiling());
+      utils.act(() => render(<App />));
+
+      expect(store).toMatchInlineSnapshot(`
+        [root]
+          ▾ <App>
+              <Count>
+              <Greeting>
+      `);
+
+      utils.act(() => triggerUpdate());
+
+      utils.act(() => store.profilerStore.stopProfiling());
+
+      const rootID = store.roots[0];
+      const {chartData} = getFlamegraphChartData(rootID, 1);
+      const allNodes = chartData.rows.flat();
+
+      expect(allNodes).toEqual([
+        expect.objectContaining({name: 'App', didRender: false}),
+        expect.objectContaining({name: 'Greeting', didRender: false}),
+        expect.objectContaining({name: 'Count', didRender: true}),
+      ]);
+    });
+  });
 });
diff --git a/packages/react-devtools-shared/src/backend/fiber/renderer.js b/packages/react-devtools-shared/src/backend/fiber/renderer.js
index bc1b2a590d59..7363c66d15c8 100644
--- a/packages/react-devtools-shared/src/backend/fiber/renderer.js
+++ b/packages/react-devtools-shared/src/backend/fiber/renderer.js
@@ -2088,6 +2088,10 @@ export function attach(
     return changedKeys;
   }

+  /**
+   * Returns true iff nextFiber actually performed any work and produced an update.
+   * For generic components, like Function or Class components, prevFiber is not considered.
+   */
   function didFiberRender(prevFiber: Fiber, nextFiber: Fiber): boolean {
     switch (nextFiber.tag) {
       case ClassComponent:
@@ -4520,7 +4524,10 @@ export function attach(
         pushOperation(convertedTreeBaseDuration);
       }

-      if (prevFiber == null || didFiberRender(prevFiber, fiber)) {
+      if (
+        prevFiber == null ||
+        (prevFiber !== fiber && didFiberRender(prevFiber, fiber))
+      ) {
         if (actualDuration != null) {
           // The actual duration reported by React includes time spent working on children.
           // This is useful information, but it's also useful to be able to exclude child durations.
@@ -5150,11 +5157,13 @@ export function attach(
           elementType === ElementTypeMemo ||
           elementType === ElementTypeForwardRef
         ) {
-          // Otherwise if this is a traced ancestor, flag for the nearest host descendant(s).
-          traceNearestHostComponentUpdate = didFiberRender(
-            prevFiber,
-            nextFiber,
-          );
+          if (prevFiber !== nextFiber) {
+            // Otherwise if this is a traced ancestor, flag for the nearest host descendant(s).
+            traceNearestHostComponentUpdate = didFiberRender(
+              prevFiber,
+              nextFiber,
+            );
+          }
         }
       }
     }
@@ -5174,18 +5183,20 @@ export function attach(
       previousSuspendedBy = fiberInstance.suspendedBy;
       // Update the Fiber so we that we always keep the current Fiber on the data.
       fiberInstance.data = nextFiber;
-      if (
-        mostRecentlyInspectedElement !== null &&
-        (mostRecentlyInspectedElement.id === fiberInstance.id ||
-          // If we're inspecting a Root, we inspect the Screen.
-          // Invalidating any Root invalidates the Screen too.
-          (mostRecentlyInspectedElement.type === ElementTypeRoot &&
-            nextFiber.tag === HostRoot)) &&
-        didFiberRender(prevFiber, nextFiber)
-      ) {
-        // If this Fiber has updated, clear cached inspected data.
-        // If it is inspected again, it may need to be re-run to obtain updated hooks values.
-        hasElementUpdatedSinceLastInspected = true;
+      if (prevFiber !== nextFiber) {
+        if (
+          mostRecentlyInspectedElement !== null &&
+          (mostRecentlyInspectedElement.id === fiberInstance.id ||
+            // If we're inspecting a Root, we inspect the Screen.
+            // Invalidating any Root invalidates the Screen too.
+            (mostRecentlyInspectedElement.type === ElementTypeRoot &&
+              nextFiber.tag === HostRoot)) &&
+          didFiberRender(prevFiber, nextFiber)
+        ) {
+          // If this Fiber has updated, clear cached inspected data.
+          // If it is inspected again, it may need to be re-run to obtain updated hooks values.
+          hasElementUpdatedSinceLastInspected = true;
+        }
       }
       // Push a new DevTools instance parent while reconciling this subtree.
       reconcilingParent = fiberInstance;
PATCH

echo "Fix applied successfully."
