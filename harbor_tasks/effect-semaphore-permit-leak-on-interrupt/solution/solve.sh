#!/usr/bin/env bash
# Gold solution: apply the fix from PR #6081 to packages/effect/src/internal/effect/circular.ts
set -euo pipefail

cd /workspace/effect

TARGET=packages/effect/src/internal/effect/circular.ts

# Idempotency guard: a distinctive line introduced by the fix.
if grep -q 'if (this.free < n) return this.take(n)' "$TARGET"; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
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

echo "Gold patch applied."
