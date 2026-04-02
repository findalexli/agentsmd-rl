#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Check if already applied
if grep -q 'putDirectMayBeIndex' src/bun.js/bindings/CookieMap.cpp; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/bindings/CookieMap.cpp b/src/bun.js/bindings/CookieMap.cpp
index fa84f709398..38b95245e08 100644
--- a/src/bun.js/bindings/CookieMap.cpp
+++ b/src/bun.js/bindings/CookieMap.cpp
@@ -7,6 +7,7 @@
 #include "HTTPParsers.h"
 #include "decodeURIComponentSIMD.h"
 #include "BunString.h"
+#include <wtf/HashSet.h>
 namespace WebCore {

 template<bool isSSL>
@@ -231,10 +232,13 @@ JSC::JSValue CookieMap::toJSON(JSC::JSGlobalObject* globalObject) const
     auto* object = JSC::constructEmptyObject(globalObject);
     RETURN_IF_EXCEPTION(scope, {});

+    HashSet<String> seenKeys;
+
     // Add modified cookies to the object
     for (const auto& cookie : m_modifiedCookies) {
         if (!cookie->value().isEmpty()) {
-            object->putDirect(vm, JSC::Identifier::fromString(vm, cookie->name()), JSC::jsString(vm, cookie->value()));
+            seenKeys.add(cookie->name());
+            object->putDirectMayBeIndex(globalObject, JSC::Identifier::fromString(vm, cookie->name()), JSC::jsString(vm, cookie->value()));
             RETURN_IF_EXCEPTION(scope, {});
         }
     }
@@ -242,8 +246,8 @@ JSC::JSValue CookieMap::toJSON(JSC::JSGlobalObject* globalObject) const
     // Add original cookies to the object
     for (const auto& cookie : m_originalCookies) {
         // Skip if this cookie name was already added from modified cookies
-        if (!object->hasProperty(globalObject, JSC::Identifier::fromString(vm, cookie.key))) {
-            object->putDirect(vm, JSC::Identifier::fromString(vm, cookie.key), JSC::jsString(vm, cookie.value));
+        if (seenKeys.add(cookie.key).isNewEntry) {
+            object->putDirectMayBeIndex(globalObject, JSC::Identifier::fromString(vm, cookie.key), JSC::jsString(vm, cookie.value));
             RETURN_IF_EXCEPTION(scope, {});
         }
     }

PATCH

echo "Patch applied successfully."
