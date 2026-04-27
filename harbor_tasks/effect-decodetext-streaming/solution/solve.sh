#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

# Idempotency: skip if already patched.
if grep -q 'decoder.decode(s, { stream: true })' packages/effect/src/internal/stream.ts; then
  echo "stream.ts already patched"
  exit 0
fi

# Apply the gold patch (inlined; never fetched from the network).
git apply <<'PATCH'
diff --git a/packages/effect/src/internal/stream.ts b/packages/effect/src/internal/stream.ts
index ada16cbe5a6..998ff55a484 100644
--- a/packages/effect/src/internal/stream.ts
+++ b/packages/effect/src/internal/stream.ts
@@ -8773,7 +8773,7 @@ export const decodeText = dual<
 >((args) => isStream(args[0]), (self, encoding = "utf-8") =>
   suspend(() => {
     const decoder = new TextDecoder(encoding)
-    return map(self, (s) => decoder.decode(s))
+    return map(self, (s) => decoder.decode(s, { stream: true }))
   }))

 /** @internal */
PATCH

echo "Patch applied successfully"
grep -n 'decoder.decode(s' packages/effect/src/internal/stream.ts
