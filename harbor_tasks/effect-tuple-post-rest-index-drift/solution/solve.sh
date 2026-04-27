#!/usr/bin/env bash
# Oracle: applies the gold patch from PR #6097 (effect-ts/effect).
# Idempotent: safely skipped if patch is already applied.
set -euo pipefail

cd /workspace/effect

# Idempotency: a distinctive line introduced by the gold patch.
if grep -q 'const index = i + j' packages/effect/src/ParseResult.ts; then
    echo "Gold patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/effect/src/ParseResult.ts b/packages/effect/src/ParseResult.ts
index b85a377aeaf..c89f8295073 100644
--- a/packages/effect/src/ParseResult.ts
+++ b/packages/effect/src/ParseResult.ts
@@ -1033,15 +1033,15 @@ const go = (ast: AST.AST, isDecoding: boolean): Parser => {
           // handle post rest elements
           // ---------------------------------------------
           for (let j = 0; j < tail.length; j++) {
-            i += j
-            if (len < i + 1) {
+            const index = i + j
+            if (len < index + 1) {
               continue
             } else {
-              const te = tail[j](input[i], options)
+              const te = tail[j](input[index], options)
               if (isEither(te)) {
                 if (Either.isLeft(te)) {
                   // the input element is present but is not valid
-                  const e = new Pointer(i, input, te.left)
+                  const e = new Pointer(index, input, te.left)
                   if (allErrors) {
                     es.push([stepKey++, e])
                     continue
@@ -1052,7 +1052,6 @@ const go = (ast: AST.AST, isDecoding: boolean): Parser => {
                 output.push([stepKey++, te.right])
               } else {
                 const nk = stepKey++
-                const index = i
                 if (!queue) {
                   queue = []
                 }
PATCH

echo "Gold patch applied successfully."
