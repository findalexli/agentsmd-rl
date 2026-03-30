#!/usr/bin/env bash
set -euo pipefail
cd /workspace/gradio

# Idempotent gold patch: add null/undefined guard to cast_value_to_type
cat > /tmp/patch.diff << 'PATCH'
diff --git a/js/dataframe/shared/utils/utils.ts b/js/dataframe/shared/utils/utils.ts
index 789ae3a530..c83e0d28ee 100644
--- a/js/dataframe/shared/utils/utils.ts
+++ b/js/dataframe/shared/utils/utils.ts
@@ -29,6 +29,9 @@ export type DataframeValue = {
  * @returns The coerced value.
  */
 export function cast_value_to_type(v: any, t: Datatype): CellValue {
+	if (v === null || v === undefined) {
+		return v;
+	}
 	if (t === "number") {
 		const n = Number(v);
 		return isNaN(n) ? v : n;
PATCH

git apply --check /tmp/patch.diff 2>/dev/null && git apply /tmp/patch.diff || echo "Patch already applied or conflicts (idempotent)"
