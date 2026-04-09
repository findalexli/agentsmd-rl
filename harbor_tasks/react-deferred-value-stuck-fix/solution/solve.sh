#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'workInProgressRootPingedLanes = mergeLanes(' packages/react-reconciler/src/ReactFiberWorkLoop.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/packages/react-reconciler/src/ReactFiberWorkLoop.js b/packages/react-reconciler/src/ReactFiberWorkLoop.js
index 15a260bc660c..6eed36e6d878 100644
--- a/packages/react-reconciler/src/ReactFiberWorkLoop.js
+++ b/packages/react-reconciler/src/ReactFiberWorkLoop.js
@@ -5040,6 +5040,13 @@ function pingSuspendedRoot(
         // the special internal exception that we use to interrupt the stack for
         // selective hydration. That was temporarily reverted but we once we add
         // it back we can use it here.
+        //
+        // In the meantime, record the pinged lanes so markRootSuspended won't
+        // mark them as suspended, allowing a retry.
+        workInProgressRootPingedLanes = mergeLanes(
+          workInProgressRootPingedLanes,
+          pingedLanes,
+        );
       }
     } else {
       // Even though we can't restart right now, we might get an
diff --git a/packages/react-reconciler/src/__tests__/ReactDeferredValue-test.js b/packages/react-reconciler/src/__tests__/ReactDeferredValue-test.js
index 3a348307f4cd..2455d344cf5c 100644
--- a/packages/react-reconciler/src/__tests__/ReactDeferredValue-test.js
+++ b/packages/react-reconciler/src/__tests__/ReactDeferredValue-test.js
@@ -1097,4 +1097,56 @@ describe('ReactDeferredValue', () => {
       expect(root).toMatchRenderedOutput(<div>B</div>);
     },
   );
+
+  // Regression test for https://github.com/facebook/react/issues/35821
+  it('deferred value catches up when a suspension is resolved during the same render', async () => {
+    let setValue;
+    function App() {
+      const [value, _setValue] = useState('initial');
+      setValue = _setValue;
+      const deferred = useDeferredValue(value);
+      return (
+        <Suspense fallback={<Text text="Loading..." />}>
+          <AsyncText text={'A:' + deferred} />
+          <Sibling text={deferred} />
+        </Suspense>
+      );
+    }
+
+    function Sibling({text}) {
+      if (text !== 'initial') {
+        // Resolve A during this render, simulating data arriving while
+        // a render is already in progress.
+        resolveText('A:' + text);
+      }
+      readText('B:' + text);
+      Scheduler.log('B: ' + text);
+      return text;
+    }
+
+    const root = ReactNoop.createRoot();
+
+    resolveText('A:initial');
+    resolveText('B:initial');
+    await act(() => root.render(<App />));
+    assertLog(['A:initial', 'B: initial']);
+
+    // Pre-resolve B so the sibling won't suspend on retry.
+    resolveText('B:updated');
+
+    await act(() => setValue('updated'));
+    assertLog([
+      // Sync render defers the value.
+      'A:initial',
+      'B: initial',
+      // Deferred render: A suspends, then Sibling resolves A mid-render.
+      'Suspend! [A:updated]',
+      'B: updated',
+      'Loading...',
+      // React retries and the deferred value catches up.
+      'A:updated',
+      'B: updated',
+    ]);
+    expect(root).toMatchRenderedOutput('A:updatedupdated');
+  });
 });
diff --git a/packages/react-reconciler/src/__tests__/ReactSuspenseWithNoopRenderer-test.js b/packages/react-reconciler/src/__tests__/ReactSuspenseWithNoopRenderer-test.js
index a5c4282e9e78..44d784788b21 100644
--- a/packages/react-reconciler/src/__tests__/ReactSuspenseWithNoopRenderer-test.js
+++ b/packages/react-reconciler/src/__tests__/ReactSuspenseWithNoopRenderer-test.js
@@ -4054,11 +4054,20 @@ describe('ReactSuspenseWithNoopRenderer', () => {
       // microtask). But this test shows an example where that's not the case.
       //
       // The fix was to check if we're in the render phase before calling
-      // `prepareFreshStack`.
+      // `prepareFreshStack`. The synchronous ping is instead recorded so the
+      // lane can be retried.
       await act(() => {
         startTransition(() => root.render(<App showMore={true} />));
       });
-      assertLog(['Suspend! [A]', 'Loading A...', 'Loading B...']);
+      assertLog([
+        'Suspend! [A]',
+        'Loading A...',
+        'Loading B...',
+        // The synchronous ping was recorded, so B retries and renders.
+        'Suspend! [A]',
+        'Loading A...',
+        'B',
+      ]);
       expect(root).toMatchRenderedOutput(<div />);
     },
   );

PATCH

echo "Patch applied successfully."
