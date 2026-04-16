#!/bin/bash
set -e

cd /workspace/airflow

# Idempotency check - skip if already patched
if grep -q "dayjs(item.x\[1\]).valueOf()" airflow-core/src/airflow/ui/src/layouts/Details/Gantt/utils.ts 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/airflow-core/src/airflow/ui/src/layouts/Details/Gantt/utils.ts b/airflow-core/src/airflow/ui/src/layouts/Details/Gantt/utils.ts
index 22df4eb28cffc..fab1d1bcf773a 100644
--- a/airflow-core/src/airflow/ui/src/layouts/Details/Gantt/utils.ts
+++ b/airflow-core/src/airflow/ui/src/layouts/Details/Gantt/utils.ts
@@ -347,8 +347,8 @@ export const createChartOptions = ({
         max:
           data.length > 0
             ? (() => {
-                const maxTime = Math.max(...data.map((item) => new Date(item.x[1] ?? "").getTime()));
-                const minTime = Math.min(...data.map((item) => new Date(item.x[0] ?? "").getTime()));
+                const maxTime = Math.max(...data.map((item) => dayjs(item.x[1]).valueOf()));
+                const minTime = Math.min(...data.map((item) => dayjs(item.x[0]).valueOf()));
                 const totalDuration = maxTime - minTime;

                 // add 5% to the max time to avoid the last tick being cut off
@@ -358,8 +358,8 @@ export const createChartOptions = ({
         min:
           data.length > 0
             ? (() => {
-                const maxTime = Math.max(...data.map((item) => new Date(item.x[1] ?? "").getTime()));
-                const minTime = Math.min(...data.map((item) => new Date(item.x[0] ?? "").getTime()));
+                const maxTime = Math.max(...data.map((item) => dayjs(item.x[1]).valueOf()));
+                const minTime = Math.min(...data.map((item) => dayjs(item.x[0]).valueOf()));
                 const totalDuration = maxTime - minTime;

                 // subtract 2% from min time so background color shows before data
PATCH

echo "Gold patch applied successfully."
