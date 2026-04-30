#!/usr/bin/env bash
set -euo pipefail

REPO=/workspace/effect
cd "$REPO"

# Idempotency guard: skip if patch already applied
if grep -q 'if (this.free < n) return this.take(n)' packages/effect/src/internal/effect/circular.ts; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/smooth-states-kick.md b/.changeset/smooth-states-kick.md
new file mode 100644
index 00000000000..20ed30f12ce
--- /dev/null
+++ b/.changeset/smooth-states-kick.md
@@ -0,0 +1,5 @@
+---
+"effect": patch
+---
+
+fix semaphore race condition where permits could be leaked
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

echo "Patch applied successfully."
