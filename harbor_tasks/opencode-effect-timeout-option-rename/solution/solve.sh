#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency check: if orElse is already used in app.tsx timeoutOrElse call, skip
if grep -q 'orElse: () => Effect.succeed(false)' packages/app/src/app.tsx; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/package.json b/package.json
index 2b1c15fb698..3b2feedf310 100644
--- a/package.json
+++ b/package.json
@@ -25,7 +25,7 @@
       "packages/slack"
     ],
     "catalog": {
-      "@effect/platform-node": "4.0.0-beta.37",
+      "@effect/platform-node": "4.0.0-beta.42",
       "@types/bun": "1.3.11",
       "@octokit/rest": "22.0.0",
       "@hono/zod-validator": "0.4.2",
@@ -45,7 +45,7 @@
       "dompurify": "3.3.1",
       "drizzle-kit": "1.0.0-beta.19-d95b7a4",
       "drizzle-orm": "1.0.0-beta.19-d95b7a4",
-      "effect": "4.0.0-beta.37",
+      "effect": "4.0.0-beta.42",
       "ai": "6.0.138",
       "hono": "4.10.7",
       "hono-openapi": "1.1.2",
diff --git a/packages/app/src/app.tsx b/packages/app/src/app.tsx
index a248ebb9446..cee915530ee 100644
--- a/packages/app/src/app.tsx
+++ b/packages/app/src/app.tsx
@@ -178,7 +178,7 @@ function ConnectionGate(props: ParentProps<{ disableHealthCheck?: boolean }>) {
           }
         }).pipe(
           effectMinDuration(checkMode() === "blocking" ? "1.2 seconds" : 0),
-          Effect.timeoutOrElse({ duration: "10 seconds", onTimeout: () => Effect.succeed(false) }),
+          Effect.timeoutOrElse({ duration: "10 seconds", orElse: () => Effect.succeed(false) }),
           Effect.ensuring(Effect.sync(() => setCheckMode("background"))),
           Effect.runPromise,
         ),
diff --git a/packages/opencode/src/effect/cross-spawn-spawner.ts b/packages/opencode/src/effect/cross-spawn-spawner.ts
index eb2560ff6f7..fc088057441 100644
--- a/packages/opencode/src/effect/cross-spawn-spawner.ts
+++ b/packages/opencode/src/effect/cross-spawn-spawner.ts
@@ -336,7 +336,7 @@ export const make = Effect.gen(function* () {
       if (Predicate.isUndefined(opts?.forceKillAfter)) return f(command, proc, signal)
       return Effect.timeoutOrElse(f(command, proc, signal), {
         duration: opts.forceKillAfter,
-        onTimeout: () => f(command, proc, "SIGKILL"),
+        orElse: () => f(command, proc, "SIGKILL"),
       })
     }

PATCH

# Update lockfile
bun install || true

echo "Patch applied successfully."
