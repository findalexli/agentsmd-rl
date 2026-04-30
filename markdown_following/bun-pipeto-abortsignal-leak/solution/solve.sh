#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Check if already applied (distinctive line from the fix)
if grep -q 'JSCallbackDataWeak' src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/bindings/webcore/AbortSignal.cpp b/src/bun.js/bindings/webcore/AbortSignal.cpp
index 888a8e490bf..7234ae4a3e0 100644
--- a/src/bun.js/bindings/webcore/AbortSignal.cpp
+++ b/src/bun.js/bindings/webcore/AbortSignal.cpp
@@ -170,6 +170,14 @@ void AbortSignal::runAbortSteps()
     for (auto& algorithm : std::exchange(m_algorithms, {}))
         algorithm.second(reason);

+    Vector<std::pair<uint32_t, Ref<AbortAlgorithm>>> abortAlgorithms;
+    {
+        Locker locker { m_abortAlgorithmsLock };
+        abortAlgorithms = std::exchange(m_abortAlgorithms, {});
+    }
+    for (auto& pair : abortAlgorithms)
+        pair.second->handleEvent(reason);
+
     // 3. Fire an event named abort at signal.
     if (hasEventListeners(eventNames().abortEvent))
         dispatchEvent(Event::create(eventNames().abortEvent, Event::CanBubble::No, Event::IsCancelable::No));
@@ -257,14 +265,18 @@ uint32_t AbortSignal::addAbortAlgorithmToSignal(AbortSignal& signal, Ref<AbortAl
         algorithm->handleEvent(signal.jsReason(*signal.scriptExecutionContext()->jsGlobalObject()));
         return 0;
     }
-    return signal.addAlgorithm([algorithm = WTF::move(algorithm)](JSC::JSValue value) mutable {
-        algorithm->handleEvent(value);
-    });
+    auto identifier = ++signal.m_algorithmIdentifier;
+    Locker locker { signal.m_abortAlgorithmsLock };
+    signal.m_abortAlgorithms.append(std::make_pair(identifier, WTF::move(algorithm)));
+    return identifier;
 }

 void AbortSignal::removeAbortAlgorithmFromSignal(AbortSignal& signal, uint32_t algorithmIdentifier)
 {
-    signal.removeAlgorithm(algorithmIdentifier);
+    Locker locker { signal.m_abortAlgorithmsLock };
+    signal.m_abortAlgorithms.removeFirstMatching([algorithmIdentifier](auto& pair) {
+        return pair.first == algorithmIdentifier;
+    });
 }

 uint32_t AbortSignal::addAlgorithm(Algorithm&& algorithm)
@@ -297,7 +309,18 @@ WebCoreOpaqueRoot root(AbortSignal* signal)

 size_t AbortSignal::memoryCost() const
 {
-    return sizeof(AbortSignal) + m_native_callbacks.sizeInBytes() + m_algorithms.sizeInBytes() + m_sourceSignals.capacity() + m_dependentSignals.capacity();
+    return sizeof(AbortSignal) + m_native_callbacks.sizeInBytes() + m_algorithms.sizeInBytes() + m_abortAlgorithms.sizeInBytes() + m_sourceSignals.capacity() + m_dependentSignals.capacity();
 }

+template<typename Visitor>
+void AbortSignal::visitAbortAlgorithms(Visitor& visitor)
+{
+    Locker locker { m_abortAlgorithmsLock };
+    for (auto& pair : m_abortAlgorithms)
+        pair.second->visitJSFunction(visitor);
+}
+
+template void AbortSignal::visitAbortAlgorithms(JSC::AbstractSlotVisitor&);
+template void AbortSignal::visitAbortAlgorithms(JSC::SlotVisitor&);
+
 } // namespace WebCore
diff --git a/src/bun.js/bindings/webcore/AbortSignal.h b/src/bun.js/bindings/webcore/AbortSignal.h
index 38c50d46682..1442edfe880 100644
--- a/src/bun.js/bindings/webcore/AbortSignal.h
+++ b/src/bun.js/bindings/webcore/AbortSignal.h
@@ -35,6 +35,7 @@
 #include "wtf/DebugHeap.h"
 #include "wtf/FastMalloc.h"
 #include <wtf/Function.h>
+#include <wtf/Lock.h>
 #include <wtf/Ref.h>
 #include <wtf/RefCounted.h>
 #include <wtf/WeakListHashSet.h>
@@ -112,6 +113,8 @@ class AbortSignal final : public RefCounted<AbortSignal>, public EventTargetWith
     uint32_t addAlgorithm(Algorithm&&);
     void removeAlgorithm(uint32_t);

+    template<typename Visitor> void visitAbortAlgorithms(Visitor&);
+
     bool isFollowingSignal() const { return !!m_followingSignal; }

     void throwIfAborted(JSC::JSGlobalObject&);
@@ -184,6 +187,12 @@ class AbortSignal final : public RefCounted<AbortSignal>, public EventTargetWith
     void eventListenersDidChange() final;

     Vector<std::pair<uint32_t, Algorithm>> m_algorithms;
+    // Kept separate from m_algorithms so the GC thread can visit the weak JS
+    // callbacks via visitAbortAlgorithms(). Erasing Ref<AbortAlgorithm> into
+    // an Algorithm lambda would hide it from the GC and reintroduce the
+    // Strong-ref cycle leak.
+    Vector<std::pair<uint32_t, Ref<AbortAlgorithm>>> m_abortAlgorithms WTF_GUARDED_BY_LOCK(m_abortAlgorithmsLock);
+    Lock m_abortAlgorithmsLock;
     WeakPtr<AbortSignal, WeakPtrImplWithEventTargetData> m_followingSignal;
     AbortSignalSet m_sourceSignals;
     AbortSignalSet m_dependentSignals;
diff --git a/src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp b/src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp
index 26e5f57f54e..80712e449d4 100644
--- a/src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp
+++ b/src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp
@@ -31,7 +31,7 @@ using namespace JSC;

 JSAbortAlgorithm::JSAbortAlgorithm(VM& vm, JSObject* callback)
     : AbortAlgorithm(jsCast<JSDOMGlobalObject*>(callback->globalObject())->scriptExecutionContext())
-    , m_data(new JSCallbackDataStrong(vm, callback, this))
+    , m_data(new JSCallbackDataWeak(vm, callback, this))
 {
 }

@@ -57,7 +57,11 @@ CallbackResult<typename IDLUndefined::ImplementationType> JSAbortAlgorithm::hand

     Ref<JSAbortAlgorithm> protectedThis(*this);

-    auto& globalObject = *jsCast<JSDOMGlobalObject*>(m_data->callback()->globalObject());
+    auto* callback = m_data->callback();
+    if (!callback)
+        return CallbackResultType::UnableToExecute;
+
+    auto& globalObject = *jsCast<JSDOMGlobalObject*>(callback->globalObject());
     auto& vm = globalObject.vm();

     JSLockHolder lock(vm);
@@ -77,6 +81,16 @@ CallbackResult<typename IDLUndefined::ImplementationType> JSAbortAlgorithm::hand
     return {};
 }

+void JSAbortAlgorithm::visitJSFunction(JSC::AbstractSlotVisitor& visitor)
+{
+    m_data->visitJSFunction(visitor);
+}
+
+void JSAbortAlgorithm::visitJSFunction(JSC::SlotVisitor& visitor)
+{
+    m_data->visitJSFunction(visitor);
+}
+
 JSC::JSValue toJS(AbortAlgorithm& impl)
 {
     if (!static_cast<JSAbortAlgorithm&>(impl).callbackData())
diff --git a/src/bun.js/bindings/webcore/JSAbortAlgorithm.h b/src/bun.js/bindings/webcore/JSAbortAlgorithm.h
index 441bfe8cce2..8c478b227ae 100644
--- a/src/bun.js/bindings/webcore/JSAbortAlgorithm.h
+++ b/src/bun.js/bindings/webcore/JSAbortAlgorithm.h
@@ -37,7 +37,7 @@ class JSAbortAlgorithm final : public AbortAlgorithm {
     ScriptExecutionContext* scriptExecutionContext() const { return ContextDestructionObserver::scriptExecutionContext(); }

     ~JSAbortAlgorithm() final;
-    JSCallbackDataStrong* callbackData() { return m_data; }
+    JSCallbackDataWeak* callbackData() { return m_data; }

     // Functions
     CallbackResult<typename IDLUndefined::ImplementationType> handleEvent(JSValue) override;
@@ -45,7 +45,10 @@ class JSAbortAlgorithm final : public AbortAlgorithm {
 private:
     JSAbortAlgorithm(JSC::VM&, JSC::JSObject* callback);

-    JSCallbackDataStrong* m_data;
+    void visitJSFunction(JSC::AbstractSlotVisitor&) override;
+    void visitJSFunction(JSC::SlotVisitor&) override;
+
+    JSCallbackDataWeak* m_data;
 };

 JSC::JSValue toJS(AbortAlgorithm&);
diff --git a/src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp b/src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp
index 59a1522462f..33095f3a9a6 100644
--- a/src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp
+++ b/src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp
@@ -77,6 +77,7 @@ template<typename Visitor>
 void JSAbortSignal::visitAdditionalChildrenInGCThread(Visitor& visitor)
 {
     wrapped().reason().visit(visitor);
+    wrapped().visitAbortAlgorithms(visitor);
 }

 DEFINE_VISIT_ADDITIONAL_CHILDREN_IN_GC_THREAD(JSAbortSignal);
diff --git a/test/js/web/streams/pipeTo-signal-leak.test.ts b/test/js/web/streams/pipeTo-signal-leak.test.ts
new file mode 100644
index 00000000000..ff2c37cd2a5
--- /dev/null
+++ b/test/js/web/streams/pipeTo-signal-leak.test.ts
@@ -0,0 +1,64 @@
+import { heapStats } from "bun:jsc";
+import { describe, expect, test } from "bun:test";
+import { expectMaxObjectTypeCount } from "harness";
+
+describe("ReadableStream.pipeTo with AbortSignal", () => {
+  // Regression: when pipeTo() is passed a signal and the pipe never completes,
+  // dropping all JS references to the signal should allow it to be collected.
+  // Previously, a Strong ref cycle (AbortSignal -> AbortAlgorithm ->
+  // Strong<callback> -> closure -> pipeState.signal -> JSAbortSignal ->
+  // Ref<AbortSignal>) caused a 100% leak.
+  test("dropping signal references should not leak AbortSignal when pipe never completes", async () => {
+    const baseline = heapStats().objectTypeCounts.AbortSignal || 0;
+    const iterations = 200;
+
+    function iteration() {
+      const controller = new AbortController();
+      const rs = new ReadableStream({
+        pull() {
+          // Never enqueue, never close: pipe stays pending forever.
+          return new Promise(() => {});
+        },
+      });
+      const ws = new WritableStream({});
+      rs.pipeTo(ws, { signal: controller.signal }).catch(() => {});
+      // All locals go out of scope here. If there is no Strong ref cycle,
+      // GC should be able to reclaim the AbortSignal.
+    }
+
+    for (let i = 0; i < iterations; i++) {
+      iteration();
+    }
+
+    // Allow microtasks to settle before GC.
+    await Bun.sleep(0);
+
+    // Allow some slack for GC timing, but nowhere near \`iterations\`.
+    await expectMaxObjectTypeCount(expect, "AbortSignal", baseline + 20);
+  });
+
+  test("aborting signal still works and cleans up after pipe completes via abort", async () => {
+    const baseline = heapStats().objectTypeCounts.AbortSignal || 0;
+    const iterations = 200;
+
+    async function iteration() {
+      const controller = new AbortController();
+      const rs = new ReadableStream({
+        pull() {
+          return new Promise(() => {});
+        },
+      });
+      const ws = new WritableStream({});
+      const p = rs.pipeTo(ws, { signal: controller.signal });
+      controller.abort();
+      await p.catch(() => {});
+    }
+
+    for (let i = 0; i < iterations; i++) {
+      await iteration();
+    }
+
+    await Bun.sleep(0);
+    await expectMaxObjectTypeCount(expect, "AbortSignal", baseline + 20);
+  });
+});

PATCH
