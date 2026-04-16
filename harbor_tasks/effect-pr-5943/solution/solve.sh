#!/bin/bash
set -e
cd /workspace/effect-checkout

# Apply the fix patch
patch -p1 <<'PATCH'
diff --git a/packages/sql-pg/src/PgClient.ts b/packages/sql-pg/src/PgClient.ts
index d0ab77f..e3fc83b 100644
--- a/packages/sql-pg/src/PgClient.ts
+++ b/packages/sql-pg/src/PgClient.ts
@@ -315,25 +315,37 @@ export const make = (
       const fiber = Option.getOrThrow(Fiber.getCurrentFiber())
       const scope = Context.unsafeGet(fiber.currentContext, Scope.Scope)
       let cause: Error | undefined = undefined
+      function onError(cause_: Error) {
+        cause = cause_
+      }
       pool.connect((err, client, release) => {
         if (err) {
           resume(Effect.fail(new SqlError({ cause: err, message: "Failed to acquire connection for transaction" })))
-        } else {
-          resume(Effect.as(
-            Scope.addFinalizer(
-              scope,
-              Effect.sync(() => {
-                client!.off("error", onError)
-                release(cause)
+          return
+        } else if (!client) {
+          resume(
+            Effect.fail(
+              new SqlError({
+                message: "Failed to acquire connection for transaction",
+                cause: new Error("No client returned")
               })
-            ),
-            client!
-          ))
-        }
-        function onError(cause_: Error) {
-          cause = cause_
+            )
+          )
+          return
         }
-        client!.on("error", onError)
+
+        // Else we know we have client defined, so we can proceed with the connection
+        client.on("error", onError)
+        resume(Effect.as(
+          Scope.addFinalizer(
+            scope,
+            Effect.sync(() => {
+              client.off("error", onError)
+              release(cause)
+            })
+          ),
+          client
+        ))
       })
     })
     const reserve = Effect.map(reserveRaw, (client) => new ConnectionImpl(client))
PATCH

# Verify the distinctive line is present
grep -q "Failed to acquire connection for transaction" packages/sql-pg/src/PgClient.ts