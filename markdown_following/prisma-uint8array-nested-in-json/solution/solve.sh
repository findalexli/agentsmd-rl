#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prisma

PARAM_FILE="packages/client/src/runtime/core/engines/client/parameterization/parameterize.ts"

if grep -q "import { deserializeJsonObject, safeJsonStringify } from '@prisma/client-engine-runtime'" "${PARAM_FILE}"; then
  echo "Patch already applied; skipping."
  exit 0
fi

git apply <<'PATCH'
diff --git a/packages/client/src/runtime/core/engines/client/parameterization/parameterize.ts b/packages/client/src/runtime/core/engines/client/parameterization/parameterize.ts
index 9619b487ce0b..3edb3402b18a 100644
--- a/packages/client/src/runtime/core/engines/client/parameterization/parameterize.ts
+++ b/packages/client/src/runtime/core/engines/client/parameterization/parameterize.ts
@@ -6,7 +6,7 @@
  * both schema rules and runtime value types agree.
  */

-import { deserializeJsonObject } from '@prisma/client-engine-runtime'
+import { deserializeJsonObject, safeJsonStringify } from '@prisma/client-engine-runtime'
 import type {
   JsonArgumentValue,
   JsonBatchQuery,
@@ -273,7 +273,7 @@ class Parameterizer {
    */
   #handleArray(items: unknown[], originalValue: unknown, edge: InputEdge): unknown {
     if (hasFlag(edge, EdgeFlag.ParamScalar) && getScalarMask(edge) & ScalarMask.Json) {
-      const jsonValue = JSON.stringify(deserializeJsonObject(items))
+      const jsonValue = safeJsonStringify(deserializeJsonObject(items))
       const type: PlaceholderType = { type: 'Json' }
       return this.#getOrCreatePlaceholder(jsonValue, type)
     }
@@ -324,7 +324,7 @@ class Parameterizer {

     const mask = getScalarMask(edge)
     if (mask & ScalarMask.Json) {
-      const jsonValue = JSON.stringify(deserializeJsonObject(obj))
+      const jsonValue = safeJsonStringify(deserializeJsonObject(obj))
       const type: PlaceholderType = { type: 'Json' }
       return this.#getOrCreatePlaceholder(jsonValue, type)
     }
PATCH

echo "Gold patch applied."
