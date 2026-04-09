#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'function onRecoverableError(error: mixed): void' packages/react-noop-renderer/src/createReactNoop.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/packages/react-noop-renderer/src/createReactNoop.js b/packages/react-noop-renderer/src/createReactNoop.js
index 79d1e1a8c9bc..99be1aae122a 100644
--- a/packages/react-noop-renderer/src/createReactNoop.js
+++ b/packages/react-noop-renderer/src/createReactNoop.js
@@ -1151,9 +1151,9 @@ function createReactNoop(reconciler: Function, useMutation: boolean) {
     }
   }

-  function onRecoverableError(error) {
-    // TODO: Turn this on once tests are fixed
-    // console.error(error);
+  function onRecoverableError(error: mixed): void {
+    // eslint-disable-next-line react-internal/warning-args, react-internal/no-production-logging -- renderer is only used for testing.
+    console.error(error);
   }
   function onDefaultTransitionIndicator(): void | (() => void) {}

diff --git a/packages/react-reconciler/src/__tests__/ReactIncrementalErrorHandling-test.internal.js b/packages/react-reconciler/src/__tests__/ReactIncrementalErrorHandling-test.internal.js
index f81a83379f8d..193ffa33889f 100644
--- a/packages/react-reconciler/src/__tests__/ReactIncrementalErrorHandling-test.internal.js
+++ b/packages/react-reconciler/src/__tests__/ReactIncrementalErrorHandling-test.internal.js
@@ -287,6 +287,10 @@ describe('ReactIncrementalErrorHandling', () => {
       'commit',
       'commit',
     ]);
+    assertConsoleErrorDev([
+      'Error: There was an error during concurrent rendering but React was able to recover by instead synchronously rendering the entire root.' +
+        '\n    in <stack>',
+    ]);
     expect(ReactNoop).toMatchRenderedOutput(
       <span prop="Everything is fine." />,
     );
@@ -339,6 +343,10 @@ describe('ReactIncrementalErrorHandling', () => {
       'commit',
       'commit',
     ]);
+    assertConsoleErrorDev([
+      'Error: There was an error during concurrent rendering but React was able to recover by instead synchronously rendering the entire root.' +
+        '\n    in <stack>',
+    ]);
     // This should not include the offscreen content
     expect(ReactNoop).toMatchRenderedOutput(
       <>
@@ -1786,6 +1794,10 @@ describe('ReactIncrementalErrorHandling', () => {
     });

     // Should finish without throwing.
+    assertConsoleErrorDev([
+      'Error: There was an error during concurrent rendering but React was able to recover by instead synchronously rendering the entire root.' +
+        '\n    in <stack>',
+    ]);
     expect(root).toMatchRenderedOutput('Everything is fine.');
   }

@@ -1832,6 +1844,10 @@ describe('ReactIncrementalErrorHandling', () => {
     });
     // Should render the final state without throwing the error.
     assertLog(['Everything is fine.']);
+    assertConsoleErrorDev([
+      'Error: There was an error during concurrent rendering but React was able to recover by instead synchronously rendering the entire root.' +
+        '\n    in <stack>',
+    ]);
     expect(root).toMatchRenderedOutput('Everything is fine.');
   }

diff --git a/packages/react-reconciler/src/__tests__/ReactIncrementalErrorReplay-test.js b/packages/react-reconciler/src/__tests__/ReactIncrementalErrorReplay-test.js
index ed4317d95706..038fee759d21 100644
--- a/packages/react-reconciler/src/__tests__/ReactIncrementalErrorReplay-test.js
+++ b/packages/react-reconciler/src/__tests__/ReactIncrementalErrorReplay-test.js
@@ -12,6 +12,7 @@

 let React;
 let ReactNoop;
+let assertConsoleErrorDev;
 let waitForAll;
 let waitForThrow;

@@ -22,6 +23,7 @@ describe('ReactIncrementalErrorReplay', () => {
     ReactNoop = require('react-noop-renderer');

     const InternalTestUtils = require('internal-test-utils');
+    assertConsoleErrorDev = InternalTestUtils.assertConsoleErrorDev;
     waitForAll = InternalTestUtils.waitForAll;
     waitForThrow = InternalTestUtils.waitForThrow;
   });
@@ -50,5 +52,9 @@ describe('ReactIncrementalErrorReplay', () => {
     }
     ReactNoop.render(<App />);
     await waitForAll([]);
+    assertConsoleErrorDev([
+      'Error: There was an error during concurrent rendering but React was able to recover by instead synchronously rendering the entire root.' +
+        '\n    in <stack>',
+    ]);
   });
 });

diff --git a/packages/react-reconciler/src/__tests__/useMemoCache-test.js b/packages/react-reconciler/src/__tests__/useMemoCache-test.js
index c07d3a6d9960..13c483a6308a 100644
--- a/packages/react-reconciler/src/__tests__/useMemoCache-test.js
+++ b/packages/react-reconciler/src/__tests__/useMemoCache-test.js
@@ -12,6 +12,7 @@ let React;
 let ReactNoop;
 let Scheduler;
 let act;
+let assertConsoleErrorDev;
 let assertLog;
 let useMemo;
 let useState;
@@ -26,8 +27,10 @@ describe('useMemoCache()', () => {
     React = require('react');
     ReactNoop = require('react-noop-renderer');
     Scheduler = require('scheduler');
-    act = require('internal-test-utils').act;
-    assertLog = require('internal-test-utils').assertLog;
+    const InternalTestUtils = require('internal-test-utils');
+    act = InternalTestUtils.act;
+    assertConsoleErrorDev = InternalTestUtils.assertConsoleErrorDev;
+    assertLog = InternalTestUtils.assertLog;
     useMemo = React.useMemo;
     useMemoCache = require('react/compiler-runtime').c;
     useState = React.useState;
@@ -256,8 +259,6 @@ describe('useMemoCache()', () => {
       return `${data.text} (n=${props.n})`;
     });

-    spyOnDev(console, 'error');
-
     const root = ReactNoop.createRoot();
     await act(() => {
       root.render(
@@ -274,6 +275,10 @@ describe('useMemoCache()', () => {
       // this triggers a throw.
       setN(1);
     });
+    assertConsoleErrorDev([
+      'Error: There was an error during concurrent rendering but React was able to recover by instead synchronously rendering the entire root.' +
+        '\n    in <stack>',
+    ]);
     expect(root).toMatchRenderedOutput('Count 0 (n=1)');
     expect(Text).toBeCalledTimes(2);
     expect(data).toBe(data0);

PATCH

echo "Patch applied successfully."
