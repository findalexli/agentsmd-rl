#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Idempotent: skip if already applied
if grep -q 'typeof direct_translation === "string" &&' js/core/src/gradio_helper.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/core/src/gradio_helper.ts b/js/core/src/gradio_helper.ts
index 84fc3d8fe4..a044841975 100644
--- a/js/core/src/gradio_helper.ts
+++ b/js/core/src/gradio_helper.ts
@@ -17,7 +17,10 @@ export function formatter(value: string | null | undefined): string {
 	}

 	const direct_translation = translate(string_value);
-	if (direct_translation !== string_value) {
+	if (
+		typeof direct_translation === "string" &&
+		direct_translation !== string_value
+	) {
 		return direct_translation;
 	}


PATCH

echo "Patch applied successfully."
