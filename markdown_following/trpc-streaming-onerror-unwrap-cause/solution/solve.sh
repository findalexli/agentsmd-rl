#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trpc

TARGET="packages/server/src/unstable-core-do-not-import/http/resolveResponse.ts"

# Idempotency: if the fix is already in place, exit cleanly.
if grep -q "getTRPCErrorFromUnknown(cause.error)" "$TARGET"; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/server/src/unstable-core-do-not-import/http/resolveResponse.ts b/packages/server/src/unstable-core-do-not-import/http/resolveResponse.ts
index 05d18e6399d..44fe5454e19 100644
--- a/packages/server/src/unstable-core-do-not-import/http/resolveResponse.ts
+++ b/packages/server/src/unstable-core-do-not-import/http/resolveResponse.ts
@@ -632,7 +632,7 @@ export async function resolveResponse<TRouter extends AnyRouter>(
         serialize: (data) => config.transformer.output.serialize(data),
         onError: (cause) => {
           opts.onError?.({
-            error: getTRPCErrorFromUnknown(cause),
+            error: getTRPCErrorFromUnknown(cause.error),
             path: undefined,
             input: undefined,
             ctx: ctxManager.valueOrUndefined(),
PATCH

echo "Patch applied successfully."
grep "getTRPCErrorFromUnknown(cause.error)" "$TARGET" >/dev/null
