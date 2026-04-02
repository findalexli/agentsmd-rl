#!/usr/bin/env bash
set -euo pipefail

AUTH_FILE="packages/opencode/src/provider/auth.ts"
PLUGIN_FILE="packages/plugin/src/index.ts"

# Idempotency check: if the spread-extra pattern already exists, skip
if grep -q '\.\.\.extra' "$AUTH_FILE" 2>/dev/null; then
  echo "Patch already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/opencode/src/provider/auth.ts b/packages/opencode/src/provider/auth.ts
index 759f8803ae8..fc4cc5e6b9c 100644
--- a/packages/opencode/src/provider/auth.ts
+++ b/packages/opencode/src/provider/auth.ts
@@ -215,12 +215,13 @@ export namespace ProviderAuth {
         }

         if ("refresh" in result) {
+          const { type: _, provider: __, refresh, access, expires, ...extra } = result
           yield* auth.set(input.providerID, {
             type: "oauth",
-            access: result.access,
-            refresh: result.refresh,
-            expires: result.expires,
-            ...(result.accountId ? { accountId: result.accountId } : {}),
+            access,
+            refresh,
+            expires,
+            ...extra,
           })
         }
       })
diff --git a/packages/plugin/src/index.ts b/packages/plugin/src/index.ts
index 7e5ae7a6ec5..8bdb51a2aec 100644
--- a/packages/plugin/src/index.ts
+++ b/packages/plugin/src/index.ts
@@ -129,6 +129,7 @@ export type AuthOuathResult = { url: string; instructions: string } & (
                 access: string
                 expires: number
                 accountId?: string
+                enterpriseUrl?: string
               }
             | { key: string }
           ))
@@ -149,6 +150,7 @@ export type AuthOuathResult = { url: string; instructions: string } & (
                 access: string
                 expires: number
                 accountId?: string
+                enterpriseUrl?: string
               }
             | { key: string }
           ))

PATCH

echo "Patch applied successfully."
