#!/bin/bash
set -euo pipefail

# Check if already applied
if grep -q "readReactElementTypeof" /workspace/react/packages/shared/ReactPerformanceTrackProperties.js 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

cd /workspace/react

git apply - <<'PATCH'
diff --git a/packages/react-reconciler/src/__tests__/ReactPerformanceTrack-test.js b/packages/react-reconciler/src/__tests__/ReactPerformanceTrack-test.js
index faaadb9cb617..5f5defb271cc 100644
--- a/packages/react-reconciler/src/__tests__/ReactPerformanceTrack-test.js
+++ b/packages/react-reconciler/src/__tests__/ReactPerformanceTrack-test.js
@@ -523,4 +523,110 @@ describe('ReactPerformanceTracks', () => {
       ],
     ]);
   });
+
+  // @gate __DEV__ && enableComponentPerformanceTrack
+  it('diffs HTML-like objects', async () => {
+    const App = function App({container}) {
+      Scheduler.unstable_advanceTime(10);
+      React.useEffect(() => {}, [container]);
+    };
+
+    class Window {}
+    const createOpaqueOriginWindow = () => {
+      return new Proxy(new Window(), {
+        get(target, prop) {
+          if (prop === Symbol.toStringTag) {
+            return target[Symbol.toStringTag];
+          }
+          // Some properties are allowed if JS itself is accessign those e.g.
+          // Symbol.toStringTag.
+          // Just make sure React isn't accessing arbitrary properties.
+          throw new Error(
+            `Failed to read named property '${String(prop)}' from Window`,
+          );
+        },
+      });
+    };
+
+    class OpaqueOriginHTMLIFrameElement {
+      constructor(textContent) {
+        this.textContent = textContent;
+      }
+      contentWindow = createOpaqueOriginWindow();
+      nodeType = 1;
+      [Symbol.toStringTag] = 'HTMLIFrameElement';
+    }
+
+    Scheduler.unstable_advanceTime(1);
+    await act(() => {
+      ReactNoop.render(
+        <App
+          container={new OpaqueOriginHTMLIFrameElement('foo')}
+          contentWindow={createOpaqueOriginWindow()}
+        />,
+      );
+    });
+
+    expect(performanceMeasureCalls).toEqual([
+      [
+        'Mount',
+        {
+          detail: {
+            devtools: {
+              color: 'warning',
+              properties: null,
+              tooltipText: 'Mount',
+              track: 'Components ⚛',
+            },
+          },
+          end: 11,
+          start: 1,
+        },
+      ],
+    ]);
+    performanceMeasureCalls.length = 0;
+
+    Scheduler.unstable_advanceTime(10);
+
+    await act(() => {
+      ReactNoop.render(
+        <App
+          container={new OpaqueOriginHTMLIFrameElement('bar')}
+          contentWindow={createOpaqueOriginWindow()}
+        />,
+      );
+    });
+
+    expect(performanceMeasureCalls).toEqual([
+      [
+        '​App',
+        {
+          detail: {
+            devtools: {
+              color: 'primary-dark',
+              properties: [
+                ['Changed Props', ''],
+                ['- container', 'HTMLIFrameElement'],
+                ['-    contentWindow', 'Window'],
+                ['-    nodeType', '1'],
+                ['-    textContent', '"foo"'],
+                ['+ container', 'HTMLIFrameElement'],
+                ['+    contentWindow', 'Window'],
+                ['+    nodeType', '1'],
+                ['+    textContent', '"bar"'],
+                [
+                  ' contentWindow',
+                  'Referentially unequal but deeply equal objects. Consider memoization.',
+                ],
+              ],
+              tooltipText: 'App',
+              track: 'Components ⚛',
+            },
+          },
+          end: 31,
+          start: 21,
+        },
+      ],
+    ]);
+  });
 });
diff --git a/packages/shared/ReactPerformanceTrackProperties.js b/packages/shared/ReactPerformanceTrackProperties.js
index 3bca2fac60fd..29aba7282f04 100644
--- a/packages/shared/ReactPerformanceTrackProperties.js
+++ b/packages/shared/ReactPerformanceTrackProperties.js
@@ -82,6 +82,13 @@ export function addObjectToProperties(
   }
 }

+function readReactElementTypeof(value: Object): mixed {
+  // Prevents dotting into $$typeof in opaque origin windows.
+  return '$$typeof' in value && hasOwnProperty.call(value, '$$typeof')
+    ? value.$$typeof
+    : undefined;
+}
+
 export function addValueToProperties(
   propertyName: string,
   value: mixed,
@@ -96,7 +103,7 @@ export function addValueToProperties(
         desc = 'null';
         break;
       } else {
-        if (value.$$typeof === REACT_ELEMENT_TYPE) {
+        if (readReactElementTypeof(value) === REACT_ELEMENT_TYPE) {
           // JSX
           const typeName = getComponentNameFromType(value.type) || '\u2026';
           const key = value.key;
@@ -352,9 +359,10 @@ export function addObjectDiffToProperties(
           typeof nextValue === 'object' &&
           prevValue !== null &&
           nextValue !== null &&
-          prevValue.$$typeof === nextValue.$$typeof
+          readReactElementTypeof(prevValue) ===
+            readReactElementTypeof(nextValue)
         ) {
-          if (nextValue.$$typeof === REACT_ELEMENT_TYPE) {
+          if (readReactElementTypeof(nextValue) === REACT_ELEMENT_TYPE) {
             if (
               prevValue.type === nextValue.type &&
               prevValue.key === nextValue.key
PATCH

echo "Patch applied successfully"
