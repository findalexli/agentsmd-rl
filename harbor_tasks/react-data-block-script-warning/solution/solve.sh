#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'isScriptDataBlock' packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js b/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js
index 94d37cfc902d..fc1039faaa0c 100644
--- a/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js
+++ b/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js
@@ -183,6 +183,7 @@ export type Props = {
   checked?: boolean,
   defaultChecked?: boolean,
   multiple?: boolean,
+  type?: string,
   src?: string | Blob | MediaSource | MediaStream, // TODO: Response
   srcSet?: string,
   loading?: 'eager' | 'lazy',
@@ -469,6 +470,44 @@ export function createHoistableInstance(
 }

 let didWarnScriptTags = false;
+function isScriptDataBlock(props: Props): boolean {
+  const scriptType = props.type;
+  if (typeof scriptType !== 'string' || scriptType === '') {
+    return false;
+  }
+  const lower = scriptType.toLowerCase();
+  // Special non-MIME keywords recognized by the HTML spec
+  // TODO: May be fine to also not warn about having these types be parsed as "parser-inserted"
+  if (
+    lower === 'module' ||
+    lower === 'importmap' ||
+    lower === 'speculationrules'
+  ) {
+    return false;
+  }
+  // JavaScript MIME types per https://mimesniff.spec.whatwg.org/#javascript-mime-type
+  switch (lower) {
+    case 'application/ecmascript':
+    case 'application/javascript':
+    case 'application/x-ecmascript':
+    case 'application/x-javascript':
+    case 'text/ecmascript':
+    case 'text/javascript':
+    case 'text/javascript1.0':
+    case 'text/javascript1.1':
+    case 'text/javascript1.2':
+    case 'text/javascript1.3':
+    case 'text/javascript1.4':
+    case 'text/javascript1.5':
+    case 'text/jscript':
+    case 'text/livescript':
+    case 'text/x-ecmascript':
+    case 'text/x-javascript':
+      return false;
+  }
+  // Any other non-empty type value means this is a data block
+  return true;
+}
 const warnedUnknownTags: {
   [key: string]: boolean,
 } = {
@@ -526,7 +565,13 @@ export function createInstance(
           // set to true and it does not execute
           const div = ownerDocument.createElement('div');
           if (__DEV__) {
-            if (enableTrustedTypesIntegration && !didWarnScriptTags) {
+            if (
+              enableTrustedTypesIntegration &&
+              !didWarnScriptTags &&
+              // Data block scripts are not executed by UAs anyway so
+              // we don't need to warn: https://html.spec.whatwg.org/multipage/scripting.html#attr-script-type
+              !isScriptDataBlock(props)
+            ) {
               console.error(
                 'Encountered a script tag while rendering React component. ' +
                   'Scripts inside React components are never executed when rendering ' +
diff --git a/packages/react-dom/src/client/__tests__/trustedTypes-test.internal.js b/packages/react-dom/src/client/__tests__/trustedTypes-test.internal.js
index 06744581ae95..2d7fa85880e7 100644
--- a/packages/react-dom/src/client/__tests__/trustedTypes-test.internal.js
+++ b/packages/react-dom/src/client/__tests__/trustedTypes-test.internal.js
@@ -248,4 +248,24 @@ describe('when Trusted Types are available in global object', () => {
       root.render(<script>alert("I am not executed")</script>);
     });
   });
+
+  it('should not warn when rendering a data block script tag', async () => {
+    const root = ReactDOMClient.createRoot(container);
+    await act(() => {
+      root.render(
+        <script type="application/json">{'{"key": "value"}'}</script>,
+      );
+    });
+  });
+
+  it('should not warn when rendering a ld+json script tag', async () => {
+    const root = ReactDOMClient.createRoot(container);
+    await act(() => {
+      root.render(
+        <script type="application/ld+json">
+          {'{"@context": "https://schema.org"}'}
+        </script>,
+      );
+    });
+  });
 });

PATCH

echo "Patch applied successfully."
