#!/bin/bash
set -e

cd /workspace/dagster

# Check if fix is already applied (idempotency)
if grep -q "_sanitize_path" python_modules/libraries/dagster-aws/dagster_aws/s3/io_manager.py; then
    echo "Fix already applied, skipping."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
--- a/python_modules/libraries/dagster-aws/dagster_aws/s3/io_manager.py
+++ b/python_modules/libraries/dagster-aws/dagster_aws/s3/io_manager.py
@@ -73,7 +73,15 @@ class PickledObjectS3IOManager(UPathIOManager):
         return {"uri": MetadataValue.path(self._uri_for_path(path))}

     def get_op_output_relative_path(self, context: InputContext | OutputContext) -> UPath:
-        return UPath("storage", super().get_op_output_relative_path(context))
+        sanitized = self._sanitize_path(super().get_op_output_relative_path(context))
+        return UPath("storage", sanitized)
+
+    @staticmethod
+    def _sanitize_path(path: UPath) -> UPath:
+        sanitized_parts = []
+        for part in path.parts:
+            sanitized_parts.append(part.replace("[", "--").replace("]", ""))
+        return UPath(*sanitized_parts)

     def _uri_for_path(self, path: UPath) -> str:
         return f"s3://{self.bucket}/{path.as_posix()}"
PATCH

echo "Patch applied successfully."
