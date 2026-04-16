#!/bin/bash
set -e

cd /workspace/airflow

# Check if patch is already applied (idempotency)
if grep -q "missing_from_serialized := set(adrq_by_dag.keys()) - ser_dag_ids" airflow-core/src/airflow/models/dag.py; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix <<'PATCH'
diff --git a/airflow-core/src/airflow/models/dag.py b/airflow-core/src/airflow/models/dag.py
index 677fbc26048e3..ad67721067c66 100644
--- a/airflow-core/src/airflow/models/dag.py
+++ b/airflow-core/src/airflow/models/dag.py
@@ -630,6 +630,10 @@ def dags_needing_dagruns(cls, session: Session) -> tuple[Any, dict[str, datetime
         you should ensure that any scheduling decisions are made in a single transaction -- as soon as the
         transaction is committed it will be unlocked.

+        For asset-triggered scheduling, Dags that have ``AssetDagRunQueue`` rows but no matching
+        ``SerializedDagModel`` row are omitted from ``triggered_date_by_dag`` until serialization exists;
+        ADRQs are **not** deleted here so the scheduler can re-evaluate on a later run.
+
         :meta private:
         """
         from airflow.models.serialized_dag import SerializedDagModel
@@ -676,6 +680,16 @@ def dag_ready(dag_id: str, cond: SerializedAssetBase, statuses: dict[UKey, bool]
             for dag_id, adrqs in adrq_by_dag.items()
         }
         ser_dags = SerializedDagModel.get_latest_serialized_dags(dag_ids=list(dag_statuses), session=session)
+        ser_dag_ids = {ser_dag.dag_id for ser_dag in ser_dags}
+        if missing_from_serialized := set(adrq_by_dag.keys()) - ser_dag_ids:
+            log.info(
+                "Dags have queued asset events (ADRQ), but are not found in the serialized_dag table."
+                " — skipping Dag run creation: %s",
+                sorted(missing_from_serialized),
+            )
+            for dag_id in missing_from_serialized:
+                del adrq_by_dag[dag_id]
+                del dag_statuses[dag_id]
         for ser_dag in ser_dags:
             dag_id = ser_dag.dag_id
             statuses = dag_statuses[dag_id]
PATCH

echo "Patch applied successfully."
