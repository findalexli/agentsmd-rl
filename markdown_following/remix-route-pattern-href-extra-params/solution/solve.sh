#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotency check — skip if already applied
if grep -qF '& Record<string, unknown>' packages/route-pattern/src/lib/types/href.ts; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply <<'PATCH'
diff --git a/packages/route-pattern/src/lib/types/href.ts b/packages/route-pattern/src/lib/types/href.ts
index 2678673d9ac..a2c1eec5e8e 100644
--- a/packages/route-pattern/src/lib/types/href.ts
+++ b/packages/route-pattern/src/lib/types/href.ts
@@ -4,12 +4,13 @@ import type * as Search from '../route-pattern/search.ts'
 type ParamValue = string | number

 // prettier-ignore
-export type HrefArgs<T extends string> =
-  [RequiredParams<T>] extends [never] ?
+export type HrefArgs<source extends string> =
+  [RequiredParams<source>] extends [never] ?
     [] | [null | undefined | Record<string, any>] | [null | undefined | Record<string, any>, Search.HrefParams] :
-    [HrefParams<T>, Search.HrefParams] | [HrefParams<T>]
+    [HrefParams<source>, Search.HrefParams] | [HrefParams<source>]

 // prettier-ignore
-type HrefParams<T extends string> =
-  Record<RequiredParams<T>, ParamValue> &
-  Partial<Record<OptionalParams<T>, ParamValue | null | undefined>>
+type HrefParams<source extends string> =
+  & Record<RequiredParams<source>, ParamValue>
+  & Partial<Record<OptionalParams<source>, ParamValue | null | undefined>>
+  & Record<string, unknown>
PATCH
