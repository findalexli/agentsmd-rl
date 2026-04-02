#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

CPP_FILE="src/bun.js/bindings/FormatStackTraceForJS.cpp"

# Idempotency: check if fix is already applied
# Base has "if (!instance->hasMaterializedErrorInfo())" — the fix changes to positive form
if grep -q 'if (instance->hasMaterializedErrorInfo())' "$CPP_FILE"; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/bindings/FormatStackTraceForJS.cpp b/src/bun.js/bindings/FormatStackTraceForJS.cpp
index 266da35c2b8..bfc5d80697d 100644
--- a/src/bun.js/bindings/FormatStackTraceForJS.cpp
+++ b/src/bun.js/bindings/FormatStackTraceForJS.cpp
@@ -691,27 +691,35 @@ JSC_DEFINE_HOST_FUNCTION(errorConstructorFuncCaptureStackTrace, (JSC::JSGlobalOb
     JSCStackTrace::getFramesForCaller(vm, callFrame, errorObject, caller, stackTrace, stackTraceLimit);

     if (auto* instance = jsDynamicCast<JSC::ErrorInstance*>(errorObject)) {
-        // Force materialization before replacing the stack frames, so that JSC's
-        // internal lazy error info mechanism doesn't later see the replaced (possibly empty)
-        // stack trace and fail to create the stack property.
-        if (!instance->hasMaterializedErrorInfo())
-            instance->materializeErrorInfoIfNeeded(vm);
-        RETURN_IF_EXCEPTION(scope, {});
-
-        instance->setStackFrames(vm, WTF::move(stackTrace));
-
-        {
-            const auto& propertyName = vm.propertyNames->stack;
-            VM::DeletePropertyModeScope deleteScope(vm, VM::DeletePropertyMode::IgnoreConfigurable);
-            DeletePropertySlot slot;
-            JSObject::deleteProperty(instance, globalObject, propertyName, slot);
-        }
-        RETURN_IF_EXCEPTION(scope, {});
-
-        if (auto* zigGlobalObject = jsDynamicCast<Zig::GlobalObject*>(globalObject)) {
-            instance->putDirectCustomAccessor(vm, vm.propertyNames->stack, zigGlobalObject->m_lazyStackCustomGetterSetter.get(zigGlobalObject), JSC::PropertyAttribute::CustomAccessor | 0);
+        if (instance->hasMaterializedErrorInfo()) {
+            // Error info was already materialized (e.g. .stack was previously accessed).
+            // Don't call setStackFrames — it would leave m_errorInfoMaterialized=true with
+            // a non-null m_stackTrace, causing ASSERT(!m_errorInfoMaterialized) in
+            // computeErrorInfo when GC's finalizeUnconditionally finds unmarked frames.
+            // Eagerly compute and set the .stack property instead.
+            OrdinalNumber line;
+            OrdinalNumber column;
+            String sourceURL;
+            JSValue result = computeErrorInfoToJSValue(vm, stackTrace, line, column, sourceURL, errorObject, nullptr);
+            RETURN_IF_EXCEPTION(scope, {});
+            errorObject->putDirect(vm, vm.propertyNames->stack, result, 0);
         } else {
-            instance->putDirectCustomAccessor(vm, vm.propertyNames->stack, CustomGetterSetter::create(vm, errorInstanceLazyStackCustomGetter, errorInstanceLazyStackCustomSetter), JSC::PropertyAttribute::CustomAccessor | 0);
+            // Not yet materialized — safe to install new frames with a lazy getter.
+            instance->setStackFrames(vm, WTF::move(stackTrace));
+
+            {
+                const auto& propertyName = vm.propertyNames->stack;
+                VM::DeletePropertyModeScope deleteScope(vm, VM::DeletePropertyMode::IgnoreConfigurable);
+                DeletePropertySlot slot;
+                JSObject::deleteProperty(instance, globalObject, propertyName, slot);
+            }
+            RETURN_IF_EXCEPTION(scope, {});
+
+            if (auto* zigGlobalObject = jsDynamicCast<Zig::GlobalObject*>(globalObject)) {
+                instance->putDirectCustomAccessor(vm, vm.propertyNames->stack, zigGlobalObject->m_lazyStackCustomGetterSetter.get(zigGlobalObject), JSC::PropertyAttribute::CustomAccessor | 0);
+            } else {
+                instance->putDirectCustomAccessor(vm, vm.propertyNames->stack, CustomGetterSetter::create(vm, errorInstanceLazyStackCustomGetter, errorInstanceLazyStackCustomSetter), JSC::PropertyAttribute::CustomAccessor | 0);
+            }
         }
     } else {
         OrdinalNumber line;

PATCH

echo "Fix applied successfully."
