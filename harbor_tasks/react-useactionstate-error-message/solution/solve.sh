#!/bin/bash
set -euo pipefail

# Check if already applied - look for the fixed error message
if grep -q "Cannot update action state while rendering" packages/react-reconciler/src/ReactFiberHooks.js 2>/dev/null; then
    echo "Fix already applied"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/packages/react-dom/src/__tests__/ReactDOMForm-test.js b/packages/react-dom/src/__tests__/ReactDOMForm-test.js
index f1a6cf791248..be4a232e4ab1 100644
--- a/packages/react-dom/src/__tests__/ReactDOMForm-test.js
+++ b/packages/react-dom/src/__tests__/ReactDOMForm-test.js
@@ -1092,7 +1092,7 @@ describe('ReactDOMForm', () => {
     const root = ReactDOMClient.createRoot(container);
     await act(async () => {
       root.render(<App />);
-      await waitForThrow('Cannot update form state while rendering.');
+      await waitForThrow('Cannot update action state while rendering.');
     });
   });

diff --git a/packages/react-reconciler/src/ReactFiberHooks.js b/packages/react-reconciler/src/ReactFiberHooks.js
index 0450495ff0d4..29c83c7d7263 100644
--- a/packages/react-reconciler/src/ReactFiberHooks.js
+++ b/packages/react-reconciler/src/ReactFiberHooks.js
@@ -2085,7 +2085,7 @@ function dispatchActionState<S, P>(
   payload: P,
 ): void {
   if (isRenderPhaseUpdate(fiber)) {
-    throw new Error('Cannot update form state while rendering.');
+    throw new Error('Cannot update action state while rendering.');
   }

   const currentAction = actionQueue.action;
diff --git a/scripts/error-codes/codes.json b/scripts/error-codes/codes.json
index 46bb2e6bccf0..09e60d8b257b 100644
--- a/scripts/error-codes/codes.json
+++ b/scripts/error-codes/codes.json
@@ -470,7 +470,7 @@
   "482": "An unknown Component is an async Client Component. Only Server Components can be async at the moment. This error is often caused by accidentally adding 'use client' to a module that was originally written for the server.",
   "483": "Hooks are not supported inside an async component. This error is often caused by accidentally adding 'use client' to a module that was originally written for the server.",
   "484": "A Server Component was postponed. The reason is omitted in production builds to avoid leaking sensitive details.",
-  "485": "Cannot update form state while rendering.",
+  "485": "Cannot update action state while rendering.",
   "486": "It should not be possible to postpone at the root. This is a bug in React.",
   "487": "We should not have any resumable nodes in the shell. This is a bug in React.",
   "488": "Couldn't find all resumable slots by key/index during replaying. The tree doesn't match so React will fallback to client rendering.",
PATCH

echo "Fix applied successfully"
