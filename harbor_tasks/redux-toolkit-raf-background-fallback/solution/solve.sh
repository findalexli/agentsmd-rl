#!/bin/bash
set -e

cd /workspace/redux-toolkit/packages/toolkit/src

# Apply the gold patch for PR #5273
cat <<'PATCH' | patch -p4
--- a/packages/toolkit/src/autoBatchEnhancer.ts
+++ b/packages/toolkit/src/autoBatchEnhancer.ts
@@ -15,6 +15,24 @@ const createQueueWithTimer = (timeout: number) => {
   }
 }

+const createRafWithFallbackTimer = (
+  raf: typeof requestAnimationFrame,
+  timeout: number,
+) => {
+  return (notify: () => void) => {
+    let called = false
+    const callback = () => {
+      if (called) return
+      called = true
+      cancelAnimationFrame(rafId)
+      clearTimeout(timerId)
+      notify()
+    }
+    const rafId = raf(callback)
+    const timerId = setTimeout(callback, timeout)
+  }
+}
+
 export type AutoBatchOptions =
   | { type: 'tick' }
   | { type: 'timer'; timeout: number }
@@ -61,7 +79,7 @@ export const autoBatchEnhancer =
         : options.type === 'raf'
           ? // requestAnimationFrame won't exist in SSR environments. Fall back to a vague approximation just to keep from erroring.
             typeof window !== 'undefined' && window.requestAnimationFrame
-            ? window.requestAnimationFrame
+            ? createRafWithFallbackTimer(window.requestAnimationFrame, 100)
             : createQueueWithTimer(10)
           : options.type === 'callback'
             ? options.queueNotification
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q "createRafWithFallbackTimer(window.requestAnimationFrame, 100)" autoBatchEnhancer.ts

echo "Patch applied successfully"
