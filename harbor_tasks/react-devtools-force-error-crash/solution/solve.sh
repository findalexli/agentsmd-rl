#!/bin/bash
set -euo pipefail

cd /workspace/react

# Check if fix is already applied (idempotency check)
if grep -q "return null;" packages/react-devtools-shared/src/backend/fiber/renderer.js && \
   ! grep -q "shouldErrorFiberAccordingToMap(fiber: any): boolean | null" packages/react-devtools-shared/src/backend/fiber/renderer.js; then
    echo "Fix appears to already be applied (partial state)"
fi

# Check if already fully applied
if grep -q "shouldErrorFiberAccordingToMap(fiber: any): boolean | null" packages/react-devtools-shared/src/backend/fiber/renderer.js && \
   grep -q "We previously simulated an error on this boundary" packages/react-reconciler/src/ReactFiberBeginWork.js; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/packages/react-devtools-shared/src/__tests__/storeForceError-test.js b/packages/react-devtools-shared/src/__tests__/storeForceError-test.js
new file mode 100644
index 000000000000..16ae50d6f028
--- /dev/null
+++ b/packages/react-devtools-shared/src/__tests__/storeForceError-test.js
@@ -0,0 +1,106 @@
+/**
+ * Copyright (c) Meta Platforms, Inc. and affiliates.
+ *
+ * This source code is licensed under the MIT license found in the
+ * LICENSE file in the root directory of this source tree.
+ *
+ * @flow
+ */
+
+import type Store from 'react-devtools-shared/src/devtools/store';
+
+import {getVersionedRenderImplementation} from './utils';
+
+describe('Store forcing errors', () => {
+  let React;
+  let agent;
+  let store: Store;
+  let utils;
+  let actAsync;
+
+  beforeEach(() => {
+    agent = global.agent;
+    store = global.store;
+    store.collapseNodesByDefault = false;
+    store.componentFilters = [];
+    store.recordChangeDescriptions = true;
+
+    React = require('react');
+    utils = require('./utils');
+
+    actAsync = utils.actAsync;
+  });
+
+  const {render} = getVersionedRenderImplementation();
+
+  // @reactVersion >= 18.0
+  it('resets forced error and fallback states when filters are changed', async () => {
+    class AnyClassComponent extends React.Component {
+      render() {
+        return this.props.children;
+      }
+    }
+
+    class ErrorBoundary extends React.Component {
+      state = {hasError: false};
+
+      static getDerivedStateFromError() {
+        return {hasError: true};
+      }
+
+      render() {
+        if (this.state.hasError) {
+          return (
+            <AnyClassComponent key="fallback">
+              <div key="did-error" />
+            </AnyClassComponent>
+          );
+        }
+        return this.props.children;
+      }
+    }
+
+    function App() {
+      return (
+        <ErrorBoundary key="content">
+          <div key="error-content" />
+        </ErrorBoundary>
+      );
+    }
+
+    await actAsync(async () => {
+      render(<App />);
+    });
+    const rendererID = utils.getRendererID();
+    await actAsync(() => {
+      agent.overrideError({
+        id: store.getElementIDAtIndex(2),
+        rendererID,
+        forceError: true,
+      });
+    });
+
+    expect(store).toMatchInlineSnapshot(`
+      [root]
+        ▾ <App>
+          ▾ <ErrorBoundary key="content">
+            ▾ <AnyClassComponent key="fallback">
+                <div key="did-error">
+    `);
+
+    await actAsync(() => {
+      agent.overrideError({
+        id: store.getElementIDAtIndex(2),
+        rendererID,
+        forceError: false,
+      });
+    });
+
+    expect(store).toMatchInlineSnapshot(`
+      [root]
+        ▾ <App>
+          ▾ <ErrorBoundary key="content">
+              <div key="error-content">
+    `);
+  });
+});
diff --git a/packages/react-devtools-shared/src/backend/fiber/renderer.js b/packages/react-devtools-shared/src/backend/fiber/renderer.js
index 49e6192b467e..aa7fe9d6ee84 100644
--- a/packages/react-devtools-shared/src/backend/fiber/renderer.js
+++ b/packages/react-devtools-shared/src/backend/fiber/renderer.js
@@ -7898,7 +7898,7 @@ export function attach(
   // Map of Fiber and its force error status: true (error), false (toggled off)
   const forceErrorForFibers = new Map<Fiber, boolean>();

-  function shouldErrorFiberAccordingToMap(fiber: any): boolean {
+  function shouldErrorFiberAccordingToMap(fiber: any): boolean | null {
     if (typeof setErrorHandler !== 'function') {
       throw new Error(
         'Expected overrideError() to not get called for earlier React versions.',
@@ -7934,7 +7934,7 @@ export function attach(
       }
     }
     if (status === undefined) {
-      return false;
+      return null;
     }
     return status;
   }
diff --git a/packages/react-reconciler/src/ReactFiberBeginWork.js b/packages/react-reconciler/src/ReactFiberBeginWork.js
index 49a4c53c8941..cf2c08236733 100644
--- a/packages/react-reconciler/src/ReactFiberBeginWork.js
+++ b/packages/react-reconciler/src/ReactFiberBeginWork.js
@@ -1584,6 +1584,9 @@ function updateClassComponent(
     // This is used by DevTools to force a boundary to error.
     switch (shouldError(workInProgress)) {
       case false: {
+        // We previously simulated an error on this boundary
+        // so the instance must have been constructed in a previous
+        // commit.
         const instance = workInProgress.stateNode;
         const ctor = workInProgress.type;
         // TODO This way of resetting the error boundary state is a hack.
PATCH

echo "Fix applied successfully"
