#!/bin/bash
# Gold solution for effect-ts/effect#6097: fix TupleWithRest post-rest index drift.
set -euo pipefail

cd /workspace/effect

# Idempotency guard — distinctive line introduced by the gold patch.
if grep -q "Fix TupleWithRest post-rest validation to check each tail index sequentially." \
     .changeset/fix-tuple-with-rest-post-rest-index-drift.md 2>/dev/null; then
  echo "[solve.sh] gold patch already applied"
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.changeset/fix-tuple-with-rest-post-rest-index-drift.md b/.changeset/fix-tuple-with-rest-post-rest-index-drift.md
new file mode 100644
index 00000000000..155671bec3f
--- /dev/null
+++ b/.changeset/fix-tuple-with-rest-post-rest-index-drift.md
@@ -0,0 +1,5 @@
+---
+"effect": patch
+---
+
+Fix TupleWithRest post-rest validation to check each tail index sequentially.
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
diff --git a/packages/effect/test/Schema/Schema/Tuple/Tuple.test.ts b/packages/effect/test/Schema/Schema/Tuple/Tuple.test.ts
index b90e1cfe526..bc5a5f489bb 100644
--- a/packages/effect/test/Schema/Schema/Tuple/Tuple.test.ts
+++ b/packages/effect/test/Schema/Schema/Tuple/Tuple.test.ts
@@ -323,6 +323,21 @@ describe("Tuple", () => {
    └─ is missing`
       )
     })
+
+    it("[String] + [Boolean, String, Number, Number] validates every post-rest index", async () => {
+      const schema = S.Tuple([S.String], S.Boolean, S.String, S.NumberFromString, S.NumberFromString)
+
+      await Util.assertions.decoding.fail(
+        schema,
+        ["a", true, "b", "1", "x"],
+        `readonly [string, ...boolean[], string, NumberFromString, NumberFromString]
+└─ [4]
+   └─ NumberFromString
+      └─ Transformation process failure
+         └─ Unable to decode "x" into a number`
+      )
+      await Util.assertions.decoding.succeed(schema, ["a", true, "b", "1", "2"], ["a", true, "b", 1, 2])
+    })
   })

   describe("encoding", () => {
PATCH

echo "[solve.sh] gold patch applied"
