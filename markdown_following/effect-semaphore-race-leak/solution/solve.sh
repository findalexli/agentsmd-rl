#!/bin/bash
set -euo pipefail

cd /workspace/effect

# Idempotency check
if grep -q "return this.take(n)" packages/effect/src/internal/effect/circular.ts; then
  echo "Fix already applied."
  exit 0
fi

# Apply the semaphore race condition fix
git apply <<'PATCH'
diff --git a/packages/effect/src/internal/effect/circular.ts b/packages/effect/src/internal/effect/circular.ts
index 67fade305a0..7f50e96f918 100644
--- a/packages/effect/src/internal/effect/circular.ts
+++ b/packages/effect/src/internal/effect/circular.ts
@@ -47,20 +47,24 @@ class Semaphore {
     core.asyncInterrupt<number>((resume) => {
       if (this.free < n) {
         const observer = () => {
-          if (this.free < n) {
-            return
-          }
+          if (this.free < n) return
           this.waiters.delete(observer)
-          this.taken += n
-          resume(core.succeed(n))
+          resume(core.suspend(() => {
+            if (this.free < n) return this.take(n)
+            this.taken += n
+            return core.succeed(n)
+          }))
         }
         this.waiters.add(observer)
         return core.sync(() => {
           this.waiters.delete(observer)
         })
       }
-      this.taken += n
-      return resume(core.succeed(n))
+      resume(core.suspend(() => {
+        if (this.free < n) return this.take(n)
+        this.taken += n
+        return core.succeed(n)
+      }))
     })

   updateTakenUnsafe(fiber: Fiber.RuntimeFiber<any, any>, f: (n: number) => number): Effect.Effect<number> {
PATCH
