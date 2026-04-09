#!/usr/bin/env bash
set -euo pipefail

cd /workspace/deno

# Idempotent: skip if already applied
if grep -q "ReflectHas" ext/web/01_dom_exception.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the fix for DOMException constructor to support options object
git apply - <<'PATCH'
diff --git a/ext/web/01_dom_exception.js b/ext/web/01_dom_exception.js
index b640e23f97f7ac..d654d07317f7ea 100644
--- a/ext/web/01_dom_exception.js
+++ b/ext/web/01_dom_exception.js
@@ -18,6 +18,7 @@ const {
   ObjectPrototypeIsPrototypeOf,
   ObjectSetPrototypeOf,
   ReflectConstruct,
+  ReflectHas,
   Symbol,
   SymbolFor,
 } = primordials;
@@ -95,21 +96,43 @@ class DOMException {
   [_code];

   // https://webidl.spec.whatwg.org/#dom-domexception-domexception
-  constructor(message = "", name = "Error") {
+  // Since Node.js allows the second argument to accept an options object, we need to support that
+  // https://github.com/nodejs/node/blob/9e201e61fd8e4b8bfb74409151cbcbbc7377ca67/lib/internal/per_context/domexception.js#L82-L96
+  constructor(message = "", options = "Error") {
     message = webidl.converters.DOMString(
       message,
       "Failed to construct 'DOMException'",
       "Argument 1",
     );
-    name = webidl.converters.DOMString(
-      name,
-      "Failed to construct 'DOMException'",
-      "Argument 2",
-    );
-    const code = nameToCodeMapping[name] ?? 0;

     // execute Error constructor to have stack property and [[ErrorData]] internal slot
     const error = ReflectConstruct(Error, [], new.target);
+
+    let name;
+    if (options !== null && typeof options === "object") {
+      name = webidl.converters.DOMString(
+        options.name,
+        "Failed to construct 'DOMException'",
+        "Argument 2",
+      );
+      if (ReflectHas(options, "cause")) {
+        ObjectDefineProperty(error, "cause", {
+          __proto__: null,
+          value: options.cause,
+          configurable: true,
+          writable: true,
+          enumerable: false,
+        });
+      }
+    } else {
+      name = webidl.converters.DOMString(
+        options,
+        "Failed to construct 'DOMException'",
+        "Argument 2",
+      );
+    }
+    const code = nameToCodeMapping[name] ?? 0;
+
     error[_message] = message;
     error[_name] = name;
     error[_code] = code;
PATCH

echo "Patch applied successfully."
