#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

# Idempotency: the gold patch adds this distinctive line to managedRuntime.ts
if grep -q "new Scheduler.SyncScheduler()" packages/effect/src/internal/managedRuntime.ts 2>/dev/null; then
    echo "Gold patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/four-yaks-exist.md b/.changeset/four-yaks-exist.md
new file mode 100644
index 00000000000..9e838a5bd4d
--- /dev/null
+++ b/.changeset/four-yaks-exist.md
@@ -0,0 +1,5 @@
+---
+"effect": patch
+---
+
+add short circuit to fiber.await internals
diff --git a/.changeset/gentle-stars-stop.md b/.changeset/gentle-stars-stop.md
new file mode 100644
index 00000000000..a0de161fa20
--- /dev/null
+++ b/.changeset/gentle-stars-stop.md
@@ -0,0 +1,5 @@
+---
+"effect": patch
+---
+
+build ManagedRuntime synchronously if possible
diff --git a/packages/effect/src/internal/fiberRuntime.ts b/packages/effect/src/internal/fiberRuntime.ts
index 8362eb2b34a..d61477c8931 100644
--- a/packages/effect/src/internal/fiberRuntime.ts
+++ b/packages/effect/src/internal/fiberRuntime.ts
@@ -451,6 +451,10 @@ export class FiberRuntime<in out A, in out E = never> extends Effectable.Class<A
   get await(): Effect.Effect<Exit.Exit<A, E>> {
     return core.async((resume) => {
       const cb = (exit: Exit.Exit<A, E>) => resume(core.succeed(exit))
+      if (this._exitValue !== null) {
+        cb(this._exitValue!)
+        return
+      }
       this.tell(
         FiberMessage.stateful((fiber, _) => {
           if (fiber._exitValue !== null) {
diff --git a/packages/effect/src/internal/managedRuntime.ts b/packages/effect/src/internal/managedRuntime.ts
index 38a2564e875..8addd717cde 100644
--- a/packages/effect/src/internal/managedRuntime.ts
+++ b/packages/effect/src/internal/managedRuntime.ts
@@ -7,6 +7,7 @@ import type * as M from "../ManagedRuntime.js"
 import { pipeArguments } from "../Pipeable.js"
 import { hasProperty } from "../Predicate.js"
 import type * as Runtime from "../Runtime.js"
+import * as Scheduler from "../Scheduler.js"
 import * as Scope from "../Scope.js"
 import type { Mutable } from "../Types.js"
 import * as core from "./core.js"
@@ -57,8 +58,9 @@ export const make = <R, ER>(
   memoMap = memoMap ?? internalLayer.unsafeMakeMemoMap()
   const scope = internalRuntime.unsafeRunSyncEffect(fiberRuntime.scopeMake())
   let buildFiber: Fiber.RuntimeFiber<Runtime.Runtime<R>, ER> | undefined
-  const runtimeEffect = core.withFiberRuntime<Runtime.Runtime<R>, ER>((fiber) => {
+  const runtimeEffect = core.suspend(() => {
     if (!buildFiber) {
+      const scheduler = new Scheduler.SyncScheduler()
       buildFiber = internalRuntime.unsafeForkEffect(
         core.tap(
           Scope.extend(
@@ -69,8 +71,9 @@ export const make = <R, ER>(
             self.cachedRuntime = rt
           }
         ),
-        { scope, scheduler: fiber.currentScheduler }
+        { scope, scheduler }
       )
+      scheduler.flush()
     }
     return core.flatten(buildFiber.await)
   })
diff --git a/packages/effect/test/ManagedRuntime.test.ts b/packages/effect/test/ManagedRuntime.test.ts
index 29549ce5f12..4b3fee526bd 100644
--- a/packages/effect/test/ManagedRuntime.test.ts
+++ b/packages/effect/test/ManagedRuntime.test.ts
@@ -76,4 +76,10 @@ describe("ManagedRuntime", () => {
     const result = Context.get(runtime.context, tag)
     strictEqual(result, "test")
   })
+
+  it("is built synchronously with runFork", () => {
+    const runtime = ManagedRuntime.make(Layer.empty)
+    runtime.runFork(Effect.void)
+    runtime.runSync(Effect.void)
+  })
 })
PATCH

echo "Gold patch applied."
