#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency check: if already patched, exit
if grep -q 'vm.interpreter.getStackTrace' src/bun.js/bindings/ErrorStackTrace.cpp 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/bindings/ErrorStackTrace.cpp b/src/bun.js/bindings/ErrorStackTrace.cpp
index b37a0e98e14..f05840f944b 100644
--- a/src/bun.js/bindings/ErrorStackTrace.cpp
+++ b/src/bun.js/bindings/ErrorStackTrace.cpp
@@ -19,6 +19,7 @@
 #include <JavaScriptCore/ErrorInstance.h>
 #include <JavaScriptCore/StackVisitor.h>
 #include <JavaScriptCore/NativeCallee.h>
+#include <JavaScriptCore/Interpreter.h>
 #include <wtf/IterationStatus.h>
 #include <JavaScriptCore/CodeBlock.h>
 #include <JavaScriptCore/FunctionCodeBlock.h>
@@ -114,144 +115,71 @@ JSCStackTrace JSCStackTrace::fromExisting(JSC::VM& vm, const WTF::Vector<JSC::St

 void JSCStackTrace::getFramesForCaller(JSC::VM& vm, JSC::CallFrame* callFrame, JSC::JSCell* owner, JSC::JSValue caller, WTF::Vector<JSC::StackFrame>& stackTrace, size_t stackTraceLimit)
 {
-    size_t framesCount = 0;
-
-    bool belowCaller = false;
-    int32_t skipFrames = 0;
-
-    WTF::String callerName {};
-    if (JSC::JSFunction* callerFunction = JSC::jsDynamicCast<JSC::JSFunction*>(caller)) {
-        callerName = callerFunction->name(vm);
-        if (callerName.isEmpty() && !callerFunction->isHostFunction() && callerFunction->jsExecutable()) {
-            callerName = callerFunction->jsExecutable()->name().string();
-        }
-    } else if (JSC::InternalFunction* callerFunctionInternal = JSC::jsDynamicCast<JSC::InternalFunction*>(caller)) {
-        callerName = callerFunctionInternal->name();
-    }
-
-    size_t totalFrames = 0;
-
-    if (!callerName.isEmpty()) {
-        JSC::StackVisitor::visit(callFrame, vm, [&](JSC::StackVisitor& visitor) -> WTF::IterationStatus {
-            if (isImplementationVisibilityPrivate(visitor)) {
-                return WTF::IterationStatus::Continue;
-            }
-
-            framesCount += 1;
-
-            // skip caller frame and all frames above it
-            if (!belowCaller) {
-                skipFrames += 1;
-
-                if (visitor->functionName() == callerName) {
-                    belowCaller = true;
-                    return WTF::IterationStatus::Continue;
-                }
-            }
-
-            totalFrames += 1;
-
-            if (totalFrames > stackTraceLimit) {
-                return WTF::IterationStatus::Done;
-            }
-
-            return WTF::IterationStatus::Continue;
-        });
-    } else if (caller && caller.isCell()) {
-        JSC::StackVisitor::visit(callFrame, vm, [&](JSC::StackVisitor& visitor) -> WTF::IterationStatus {
-            if (isImplementationVisibilityPrivate(visitor)) {
-                return WTF::IterationStatus::Continue;
-            }
-
-            framesCount += 1;
-
-            // skip caller frame and all frames above it
-            if (!belowCaller) {
-                auto callee = visitor->callee();
-                skipFrames += 1;
-                if (callee.isCell() && callee.asCell() == caller) {
-                    belowCaller = true;
-                    return WTF::IterationStatus::Continue;
-                }
-            }
-
-            totalFrames += 1;
-
-            if (totalFrames > stackTraceLimit) {
-                return WTF::IterationStatus::Done;
-            }
-
-            return WTF::IterationStatus::Continue;
-        });
-    } else if (caller.isEmpty() || caller.isUndefined()) {
-        // Skip the first frame.
-        JSC::StackVisitor::visit(callFrame, vm, [&](JSC::StackVisitor& visitor) -> WTF::IterationStatus {
-            if (isImplementationVisibilityPrivate(visitor)) {
-                return WTF::IterationStatus::Continue;
-            }
-
-            framesCount += 1;
-
-            if (!belowCaller) {
-                skipFrames += 1;
-                belowCaller = true;
-            }
-
-            totalFrames += 1;
-
-            if (totalFrames > stackTraceLimit) {
-                return WTF::IterationStatus::Done;
-            }
-
-            return WTF::IterationStatus::Continue;
-        });
-    }
-    size_t i = 0;
-    totalFrames = 0;
-    stackTrace.reserveInitialCapacity(framesCount);
-    JSC::StackVisitor::visit(callFrame, vm, [&](JSC::StackVisitor& visitor) -> WTF::IterationStatus {
-        // Skip native frames
-        if (isImplementationVisibilityPrivate(visitor)) {
-            return WTF::IterationStatus::Continue;
-        }
-
-        // Skip frames if needed
-        if (skipFrames > 0) {
-            skipFrames--;
-            return WTF::IterationStatus::Continue;
+    UNUSED_PARAM(callFrame);
+
+    // Delegate to Interpreter::getStackTrace which includes async stack frames
+    // (from the await chain via getAsyncStackTrace). The previous hand-rolled
+    // StackVisitor::visit walk only collected synchronous frames.
+    //
+    // We always collect with framesToSkip=1 (to drop Error.captureStackTrace
+    // itself) and without the caller argument, because Interpreter::getStackTrace's
+    // built-in caller filtering skips entry-frame tracking during the skip phase,
+    // which loses async frames when the caller is the innermost sync frame.
+    // Instead we filter out frames up to and including the caller afterwards.
+    //
+    // Collect without a limit: stackTraceLimit must apply to visible frames
+    // AFTER Bun's post-filter and AFTER caller removal, not to raw frames from
+    // JSC. If the caller is deep, capping at stackTraceLimit here would collect
+    // only frames that get removed, leaving an empty trace. Stack depth is
+    // bounded by native stack size so this walk is still O(actual depth).
+    WTF::Vector<JSC::StackFrame> rawFrames;
+    vm.interpreter.getStackTrace(owner, rawFrames, 1, std::numeric_limits<size_t>::max());
+
+    // JSC's getStackTrace uses StackVisitor::isImplementationVisibilityPrivate
+    // which differs from Bun's helper — post-filter to keep behavior consistent
+    // with new Error() stack formatting.
+    stackTrace.reserveInitialCapacity(rawFrames.size());
+    for (auto& frame : rawFrames) {
+        if (!isImplementationVisibilityPrivate(frame))
+            stackTrace.append(WTF::move(frame));
+    }
+
+    if (!caller.isObject()) {
+        if (stackTrace.size() > stackTraceLimit)
+            stackTrace.shrink(stackTraceLimit);
+        return;
+    }
+
+    JSC::JSObject* callerObject = caller.getObject();
+    auto* globalObject = callerObject->globalObject();
+    WTF::String callerName = Zig::functionName(vm, globalObject, callerObject);
+
+    // Match V8: remove all frames up to and including the caller. If the caller
+    // is not found anywhere in the sync portion of the stack, remove everything.
+    // We match by cell identity first, then by name — name matching is needed
+    // because a resumed async function's frame callee is the generator's `next`
+    // function (a different cell) but Zig::functionName still reports the
+    // original async function's name.
+    size_t removeCount = stackTrace.size();
+    for (size_t i = 0; i < stackTrace.size(); i++) {
+        const auto& frame = stackTrace.at(i);
+        if (frame.isAsyncFrame())
+            break;
+        if (frame.callee() == callerObject) {
+            removeCount = i + 1;
+            break;
         }
-
-        totalFrames += 1;
-
-        if (totalFrames > stackTraceLimit) {
-            return WTF::IterationStatus::Done;
+        if (!callerName.isEmpty() && Zig::functionName(vm, globalObject, frame, FinalizerSafety::NotInFinalizer, nullptr) == callerName) {
+            removeCount = i + 1;
+            break;
         }
+    }

-        if (visitor->isNativeCalleeFrame()) {
-
-            auto* nativeCallee = visitor->callee().asNativeCallee();
-            switch (nativeCallee->category()) {
-            case NativeCallee::Category::Wasm: {
-                stackTrace.append(StackFrame(visitor->wasmFunctionIndexOrName()));
-                break;
-            }
-            case NativeCallee::Category::InlineCache: {
-                break;
-            }
-            }
-#if USE(ALLOW_LINE_AND_COLUMN_NUMBER_IN_BUILTINS)
-        } else if (!!visitor->codeBlock())
-#else
-            } else if (!!visitor->codeBlock() && !visitor->codeBlock()->unlinkedCodeBlock()->isBuiltinFunction())
-#endif
-            stackTrace.append(StackFrame(vm, owner, visitor->callee().asCell(), visitor->codeBlock(), visitor->bytecodeIndex()));
-        else
-            stackTrace.append(StackFrame(vm, owner, visitor->callee().asCell()));
-
-        i++;
+    if (removeCount > 0)
+        stackTrace.removeAt(0, removeCount);

-        return (i == framesCount) ? WTF::IterationStatus::Done : WTF::IterationStatus::Continue;
-    });
+    if (stackTrace.size() > stackTraceLimit)
+        stackTrace.shrink(stackTraceLimit);
 }

 JSCStackTrace JSCStackTrace::getStackTraceForThrownValue(JSC::VM& vm, JSC::JSValue thrownValue)

PATCH
