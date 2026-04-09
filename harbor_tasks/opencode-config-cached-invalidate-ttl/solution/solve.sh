#!/usr/bin/env bash
set -euo pipefail

cd /repo

FILE="packages/opencode/src/config/config.ts"

# Idempotency check: if cachedInvalidateWithTTL is already present, patch is applied
if grep -q 'cachedInvalidateWithTTL' "$FILE"; then
  echo "Patch already applied."
  # Ensure changes are committed for git clean test
  if [ -n "$(git status --porcelain)" ]; then
    git add -A && git commit -m "Apply fix: Use cachedInvalidateWithTTL with error logging" || true
  fi
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/config/config.ts b/packages/opencode/src/config/config.ts
index 645ae8814ad..67f298b427e 100644
--- a/packages/opencode/src/config/config.ts
+++ b/packages/opencode/src/config/config.ts
@@ -40,7 +40,7 @@ import { Lock } from "@/util/lock"
 import { AppFileSystem } from "@/filesystem"
 import { InstanceState } from "@/effect/instance-state"
 import { makeRuntime } from "@/effect/run-service"
-import { Effect, Layer, ServiceMap } from "effect"
+import { Duration, Effect, Layer, ServiceMap } from "effect"
 
 export namespace Config {
   const ModelId = z.string().meta({ $ref: "https://models.dev/model-schema.json#/$defs/Model" })
@@ -1241,7 +1241,15 @@ export namespace Config {
         return result
       })
 
-      let cachedGlobal = yield* Effect.cached(loadGlobal().pipe(Effect.orElseSucceed(() => ({}) as Info)))
+      const [cachedGlobal, invalidateGlobal] = yield* Effect.cachedInvalidateWithTTL(
+        loadGlobal().pipe(
+          Effect.tapError((error) =>
+            Effect.sync(() => log.error("failed to load global config, using defaults", { error: String(error) })),
+          ),
+          Effect.orElseSucceed((): Info => ({}),
+        ),
+        Duration.infinity,
+      )
 
       const getGlobal = Effect.fn("Config.getGlobal")(function* () {
         return yield* cachedGlobal
@@ -1446,7 +1454,7 @@ export namespace Config {
       })
 
       const invalidate = Effect.fn("Config.invalidate")(function* (wait?: boolean) {
-        cachedGlobal = yield* Effect.cached(loadGlobal().pipe(Effect.orElseSucceed(() => ({}) as Info)))
+        yield* invalidateGlobal
         const task = Instance.disposeAll()
           .catch(() => undefined)
           .finally(() =>
PATCH

echo "Patch applied successfully."

# Commit the changes to ensure clean git state for tests
git add -A && git commit -m "Apply fix: Use cachedInvalidateWithTTL with error logging" || true
