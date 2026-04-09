#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'primaryChildFragment.sibling' packages/react-reconciler/src/ReactFiberNewContext.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-reconciler/src/ReactFiberNewContext.js b/packages/react-reconciler/src/ReactFiberNewContext.js
index 193cf74d3bec..ac9d766d6ae3 100644
--- a/packages/react-reconciler/src/ReactFiberNewContext.js
+++ b/packages/react-reconciler/src/ReactFiberNewContext.js
@@ -323,12 +323,23 @@ function propagateContextChanges<T>(
         renderLanes,
         workInProgress,
       );
-      if (!forcePropagateEntireTree) {
-        // During lazy propagation, we can defer propagating changes to
-        // the children, same as the consumer match above.
-        nextFiber = null;
+      // The primary children's fibers may not exist in the tree (they
+      // were discarded on initial mount if they suspended). However, the
+      // fallback children ARE in the committed tree and visible to the
+      // user. We need to continue propagating into the fallback subtree
+      // so that its context consumers are marked for re-render.
+      //
+      // The fiber structure is:
+      //   SuspenseComponent
+      //     -> child: OffscreenComponent (primary, hidden)
+      //       -> sibling: FallbackFragment
+      //
+      // Skip the primary (hidden) subtree and jump to the fallback.
+      const primaryChildFragment = fiber.child;
+      if (primaryChildFragment !== null) {
+        nextFiber = primaryChildFragment.sibling;
       } else {
-        nextFiber = fiber.child;
+        nextFiber = null;
       }
     } else {
       // Traverse down.
diff --git a/packages/react-reconciler/src/__tests__/ReactContextPropagation-test.js b/packages/react-reconciler/src/__tests__/ReactContextPropagation-test.js
index 8fe57a2e50de..6a2b74813e15 100644
--- a/packages/react-reconciler/src/__tests__/ReactContextPropagation-test.js
+++ b/packages/react-reconciler/src/__tests__/ReactContextPropagation-test.js
@@ -1037,4 +1037,80 @@ describe('ReactLazyContextPropagation', () => {
     assertLog(['Result']);
     expect(root).toMatchRenderedOutput('Result');
   });
+
+  // @gate enableLegacyCache
+  it('context change propagates to Suspense fallback (memo boundary)', async () => {
+    // When a context change occurs above a Suspense boundary that is currently
+    // showing its fallback, the fallback's context consumers should re-render
+    // with the updated value - even if there's a memo boundary between the
+    // provider and the Suspense boundary that prevents the fallback element
+    // references from changing.
+    const root = ReactNoop.createRoot();
+    const Context = React.createContext('A');
+
+    let setContext;
+    function App() {
+      const [value, _setValue] = useState('A');
+      setContext = _setValue;
+      return (
+        <Context.Provider value={value}>
+          <MemoizedWrapper />
+          <Text text={value} />
+        </Context.Provider>
+      );
+    }
+
+    const MemoizedWrapper = React.memo(function MemoizedWrapper() {
+      return (
+        <Suspense fallback={<FallbackConsumer />}>
+          <AsyncChild />
+        </Suspense>
+      );
+    });
+
+    function FallbackConsumer() {
+      const value = useContext(Context);
+      return <Text text={'Fallback: ' + value} />;
+    }
+
+    function AsyncChild() {
+      readText('async');
+      return <Text text="Content" />;
+    }
+
+    // Initial render - primary content suspends, fallback is shown
+    await act(() => {
+      root.render(<App />);
+    });
+    assertLog([
+      'Suspend! [async]',
+      'Fallback: A',
+      'A',
+      // pre-warming
+      'Suspend! [async]',
+    ]);
+    expect(root).toMatchRenderedOutput('Fallback: AA');
+
+    // Update context while still suspended. The fallback consumer should
+    // re-render with the new value.
+    await act(() => {
+      setContext('B');
+    });
+    assertLog([
+      // The Suspense boundary retries the primary children first
+      'Suspend! [async]',
+      'Fallback: B',
+      'B',
+      // pre-warming
+      'Suspend! [async]',
+    ]);
+    expect(root).toMatchRenderedOutput('Fallback: BB');
+
+    // Unsuspend. The primary content should render with the latest context.
+    await act(async () => {
+      await resolveText('async');
+    });
+    assertLog(['Content']);
+    expect(root).toMatchRenderedOutput('ContentB');
+  });
 });

PATCH

echo "Patch applied successfully."
