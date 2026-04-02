#!/usr/bin/env bash
set -euo pipefail

HEADER="src/bun.js/bindings/NodeVMScriptFetcher.h"

# Idempotency: skip if already fixed
if grep -q 'Weak<JSC::JSCell> m_owner' "$HEADER" 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/bindings/NodeVMScriptFetcher.h b/src/bun.js/bindings/NodeVMScriptFetcher.h
index b8676b2445c..7275d906f5a 100644
--- a/src/bun.js/bindings/NodeVMScriptFetcher.h
+++ b/src/bun.js/bindings/NodeVMScriptFetcher.h
@@ -3,6 +3,8 @@
 #include "root.h"

 #include <JavaScriptCore/ScriptFetcher.h>
+#include <JavaScriptCore/Weak.h>
+#include <JavaScriptCore/WeakInlines.h>
 #include <wtf/Scope.h>

 namespace Bun {
@@ -16,8 +18,19 @@ class NodeVMScriptFetcher : public JSC::ScriptFetcher {

     JSC::JSValue dynamicImportCallback() const { return m_dynamicImportCallback.get(); }

-    JSC::JSValue owner() const { return m_owner.get(); }
-    void owner(JSC::VM& vm, JSC::JSValue value) { m_owner.set(vm, value); }
+    JSC::JSValue owner() const
+    {
+        if (auto* cell = m_owner.get())
+            return JSC::JSValue(cell);
+        return JSC::jsUndefined();
+    }
+    void owner(JSC::VM&, JSC::JSValue value)
+    {
+        if (value.isCell())
+            m_owner = JSC::Weak<JSC::JSCell>(value.asCell());
+        else
+            m_owner.clear();
+    }

     bool isUsingDefaultLoader() const { return m_isUsingDefaultLoader; }
     auto temporarilyUseDefaultLoader()
@@ -30,13 +43,20 @@ class NodeVMScriptFetcher : public JSC::ScriptFetcher {

 private:
     JSC::Strong<JSC::Unknown> m_dynamicImportCallback;
-    JSC::Strong<JSC::Unknown> m_owner;
+    // m_owner is the NodeVMScript / JSFunction / module wrapper that holds this
+    // fetcher via m_source -> SourceProvider -> SourceOrigin -> RefPtr<fetcher>.
+    // A Strong handle here would form an uncollectable cycle (the owner keeps
+    // the fetcher alive via RefPtr, and the fetcher would keep the owner alive
+    // as a GC root). Use Weak instead: when the owner is collected its
+    // SourceCode chain drops the last RefPtr to this fetcher.
+    JSC::Weak<JSC::JSCell> m_owner;
     bool m_isUsingDefaultLoader = false;

     NodeVMScriptFetcher(JSC::VM& vm, JSC::JSValue dynamicImportCallback, JSC::JSValue owner)
         : m_dynamicImportCallback(vm, dynamicImportCallback)
-        , m_owner(vm, owner)
     {
+        if (owner.isCell())
+            m_owner = JSC::Weak<JSC::JSCell>(owner.asCell());
     }
 };

PATCH

echo "Patch applied successfully."
