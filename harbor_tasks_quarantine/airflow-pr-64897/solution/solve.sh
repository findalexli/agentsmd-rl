#!/bin/bash
set -e

cd /workspace/airflow

# Idempotency check - skip if already patched (look for the specific patch line)
if grep -q '"partition_key",  # Airflow 3.2+' providers/openlineage/src/airflow/providers/openlineage/utils/utils.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/providers/openlineage/src/airflow/providers/openlineage/utils/utils.py b/providers/openlineage/src/airflow/providers/openlineage/utils/utils.py
index 1234567..abcdefg 100644
--- a/providers/openlineage/src/airflow/providers/openlineage/utils/utils.py
+++ b/providers/openlineage/src/airflow/providers/openlineage/utils/utils.py
@@ -744,6 +744,8 @@ class DagRunInfo(InfoJsonEncodable):
         "execution_date",  # Airflow 2
         "external_trigger",  # Removed in Airflow 3
         "logical_date",  # Airflow 3
+        "partition_key",  # Airflow 3.2+
+        "partition_date",  # Airflow 3.2+
         "run_after",  # Airflow 3
         "run_id",
         "run_type",
PATCH

echo "Patch applied successfully."
