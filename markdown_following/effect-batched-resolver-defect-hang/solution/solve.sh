#!/bin/bash
set -euo pipefail

cd /workspace/effect

if grep -q "ensuring(" packages/effect/src/internal/fiberRuntime.ts && \
   grep -q "fix-batched-resolver-defect-hang" .changeset/fix-batched-resolver-defect-hang.md 2>/dev/null; then
    echo "solve.sh: already applied, exiting"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/fix-batched-resolver-defect-hang.md b/.changeset/fix-batched-resolver-defect-hang.md
new file mode 100644
index 00000000000..0b35a6dce00
--- /dev/null
+++ b/.changeset/fix-batched-resolver-defect-hang.md
@@ -0,0 +1,7 @@
+---
+"effect": patch
+---
+
+Fix batched request resolver defects causing consumer fibers to hang forever.
+
+When a `RequestResolver.makeBatched` resolver died with a defect, the request `Deferred`s were never completed because the cleanup logic in `invokeWithInterrupt` used `flatMap` (which only runs on success). Changed to `ensuring` so uncompleted request entries are always resolved regardless of exit type.
diff --git a/packages/effect/src/internal/fiberRuntime.ts b/packages/effect/src/internal/fiberRuntime.ts
index eaa1e32b973..f93e75c92f9 100644
--- a/packages/effect/src/internal/fiberRuntime.ts
+++ b/packages/effect/src/internal/fiberRuntime.ts
@@ -3722,7 +3722,7 @@ export const invokeWithInterrupt: <A, E, R>(
   onInterrupt?: () => void
 ) =>
   core.fiberIdWith((id) =>
-    core.flatMap(
+    ensuring(
       core.flatMap(
         forkDaemon(core.interruptible(self)),
         (processing) =>
@@ -3770,19 +3770,18 @@ export const invokeWithInterrupt: <A, E, R>(
             })
           })
       ),
-      () =>
-        core.suspend(() => {
-          const residual = entries.flatMap((entry) => {
-            if (!entry.state.completed) {
-              return [entry]
-            }
-            return []
-          })
-          return core.forEachSequentialDiscard(
-            residual,
-            (entry) => complete(entry.request as any, core.exitInterrupt(id))
-          )
+      core.suspend(() => {
+        const residual = entries.flatMap((entry) => {
+          if (!entry.state.completed) {
+            return [entry]
+          }
+          return []
         })
+        return core.forEachSequentialDiscard(
+          residual,
+          (entry) => complete(entry.request as any, core.exitInterrupt(id))
+        )
+      })
     )
   )

PATCH

echo "solve.sh: gold patch applied"
