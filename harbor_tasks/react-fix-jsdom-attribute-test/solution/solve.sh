#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Check if already applied (JSDOM setAttribute hack)
if grep -q "Fix JSDOM. setAttribute is supposed to throw" packages/react-dom/src/__tests__/ReactDOMAttribute-test.js; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/packages/react-dom/src/__tests__/ReactDOMAttribute-test.js b/packages/react-dom/src/__tests__/ReactDOMAttribute-test.js
index 63baa38c7101..af128d180e8d 100644
--- a/packages/react-dom/src/__tests__/ReactDOMAttribute-test.js
+++ b/packages/react-dom/src/__tests__/ReactDOMAttribute-test.js
@@ -9,6 +9,13 @@

 'use strict';

+// Fix JSDOM. setAttribute is supposed to throw on things that can't be implicitly toStringed.
+const setAttribute = Element.prototype.setAttribute;
+Element.prototype.setAttribute = function (name, value) {
+  // eslint-disable-next-line react-internal/safe-string-coercion
+  return setAttribute.call(this, name, '' + value);
+};
+
 describe('ReactDOM unknown attribute', () => {
   let React;
   let ReactDOMClient;
@@ -171,13 +178,7 @@ describe('ReactDOM unknown attribute', () => {
       const test = () =>
         testUnknownAttributeAssignment(new TemporalLike(), null);

-      if (gate('enableTrustedTypesIntegration') && !__DEV__) {
-        // TODO: this still throws in DEV even though it's not toString'd in prod.
-        await expect(test).rejects.toThrowError('2020-01-01');
-      } else {
-        await expect(test).rejects.toThrowError(new TypeError('prod message'));
-      }
-
+      await expect(test).rejects.toThrowError(new TypeError('prod message'));
       assertConsoleErrorDev([
         'The provided `unknown` attribute is an unsupported type TemporalLike.' +
           ' This value must be coerced to a string before using it here.\n' +
diff --git a/packages/shared/CheckStringCoercion.js b/packages/shared/CheckStringCoercion.js
index 0165d8b19c1f..a186d6755d99 100644
--- a/packages/shared/CheckStringCoercion.js
+++ b/packages/shared/CheckStringCoercion.js
@@ -76,8 +76,6 @@ export function checkAttributeStringCoercion(
   attributeName: string,
 ): void | string {
   if (__DEV__) {
-    // TODO: for enableTrustedTypesIntegration we don't toString this
-    //       so we shouldn't need the DEV warning.
     if (willCoercionThrow(value)) {
       console.error(
         'The provided `%s` attribute is an unsupported type %s.' +
PATCH

echo "Fix applied successfully"
