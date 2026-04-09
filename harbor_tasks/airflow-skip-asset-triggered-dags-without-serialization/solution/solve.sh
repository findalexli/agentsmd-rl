#!/bin/bash
set -e

cd /workspace/airflow

# Check if already patched (idempotency check)
if grep -q "missing_from_serialized := set(adrq_by_dag.keys()) - ser_dag_ids" airflow-core/src/airflow/models/dag.py; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
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
diff --git a/airflow-core/tests/unit/models/test_dag.py b/airflow-core/tests/unit/models/test_dag.py
index 046c85ea79901..00a0f1a1ef2da 100644
--- a/airflow-core/tests/unit/models/test_dag.py
+++ b/airflow-core/tests/unit/models/test_dag.py
@@ -33,7 +33,7 @@
 import pendulum
 import pytest
 import time_machine
-from sqlalchemy import delete, inspect, select, update
+from sqlalchemy import delete, func, inspect, select, update

 from airflow import settings
 from airflow._shared.module_loading import qualname
@@ -2047,6 +2047,134 @@ def test_dags_needing_dagruns_assets(self, dag_maker, session):
         dag_models = query.all()
         assert dag_models == [dag_model]

+    def test_dags_needing_dagruns_skips_adrq_when_serialized_dag_missing(
+        self, session, caplog, testing_dag_bundle
+    ):
+        """ADRQ rows for a Dag without SerializedDagModel must be skipped (no triggered_date_by_dag).
+
+        Rows must remain in ``asset_dag_run_queue`` so the scheduler can re-evaluate on a later run once
+        ``SerializedDagModel`` exists (``dags_needing_dagruns`` only drops them from the in-memory
+        candidate set, it does not delete ORM rows).
+        """
+        orphan_dag_id = "adrq_no_serialized_dag"
+        orphan_uri = "test://asset_for_orphan_adrq"
+        session.add(AssetModel(uri=orphan_uri))
+        session.flush()
+        asset_id = session.scalar(select(AssetModel.id).where(AssetModel.uri == orphan_uri))
+
+        dag_model = DagModel(
+            dag_id=orphan_dag_id,
+            bundle_name="testing",
+            max_active_tasks=1,
+            has_task_concurrency_limits=False,
+            max_consecutive_failed_dag_runs=0,
+            next_dagrun=timezone.datetime(2038, 1, 1),
+            next_dagrun_create_after=timezone.datetime(2038, 1, 2),
+            is_stale=False,
+            has_import_errors=False,
+            is_paused=False,
+            asset_expression={"any": [{"uri": orphan_uri}]},
+        )
+        session.add(dag_model)
+        session.flush()
+
+        session.add(AssetDagRunQueue(asset_id=asset_id, target_dag_id=orphan_dag_id))
+        session.flush()
+
+        with caplog.at_level(logging.DEBUG, logger="airflow.models.dag"):
+            _query, triggered_date_by_dag = DagModel.dags_needing_dagruns(session)
+
+        assert orphan_dag_id not in triggered_date_by_dag
+        assert (
+            "Dags have queued asset events (ADRQ), but are not found in the serialized_dag table."
+            in caplog.text
+        )
+        assert orphan_dag_id in caplog.text
+        assert (
+            session.scalar(
+                select(func.count())
+                .select_from(AssetDagRunQueue)
+                .where(AssetDagRunQueue.target_dag_id == orphan_dag_id)
+            )
+            == 1
+        )
+
+    def test_dags_needing_dagruns_missing_serialized_debug_lists_sorted_dag_ids(
+        self, session, caplog, testing_dag_bundle
+    ):
+        """When multiple dags lack SerializedDagModel, the debug log lists dag_ids sorted."""
+        session.add_all(
+            [
+                AssetModel(uri="test://ds_ghost_z"),
+                AssetModel(uri="test://ds_ghost_a"),
+            ]
+        )
+        session.flush()
+        id_z = session.scalar(select(AssetModel.id).where(AssetModel.uri == "test://ds_ghost_z"))
+        id_a = session.scalar(select(AssetModel.id).where(AssetModel.uri == "test://ds_ghost_a"))
+        far = timezone.datetime(2038, 1, 1)
+        far_after = timezone.datetime(2038, 1, 2)
+        session.add_all(
+            [
+                DagModel(
+                    dag_id="ghost_z",
+                    bundle_name="testing",
+                    max_active_tasks=1,
+                    has_task_concurrency_limits=False,
+                    max_consecutive_failed_dag_runs=0,
+                    next_dagrun=far,
+                    next_dagrun_create_after=far_after,
+                    is_stale=False,
+                    has_import_errors=False,
+                    is_paused=False,
+                    asset_expression={"any": [{"uri": "test://ds_ghost_z"}]},
+                ),
+                DagModel(
+                    dag_id="ghost_a",
+                    bundle_name="testing",
+                    max_active_tasks=1,
+                    has_task_concurrency_limits=False,
+                    max_consecutive_failed_dag_runs=0,
+                    next_dagrun=far,
+                    next_dagrun_create_after=far_after,
+                    is_stale=False,
+                    has_import_errors=False,
+                    is_paused=False,
+                    asset_expression={"any": [{"uri": "test://ds_ghost_a"}]},
+                ),
+            ]
+        )
+        session.flush()
+
+        session.add_all(
+            [
+                AssetDagRunQueue(asset_id=id_z, target_dag_id="ghost_z"),
+                AssetDagRunQueue(asset_id=id_a, target_dag_id="ghost_a"),
+            ]
+        )
+        session.flush()
+
+        with caplog.at_level(logging.DEBUG, logger="airflow.models.dag"):
+            _query, triggered_date_by_dag = DagModel.dags_needing_dagruns(session)
+
+        assert "ghost_a" not in triggered_date_by_dag
+        assert "ghost_z" not in triggered_date_by_dag
+        msg = next(
+            r.message
+            for r in caplog.records
+            if "Dags have queued asset events (ADRQ), but are not found in the serialized_dag table."
+            in r.message
+        )
+        assert msg.index("ghost_a") < msg.index("ghost_z")
+        assert (
+            session.scalar(
+                select(func.count())
+                .select_from(AssetDagRunQueue)
+                .where(AssetDagRunQueue.target_dag_id.in_(("ghost_a", "ghost_z")))
+            )
+            == 2
+        )
+
     def test_dags_needing_dagruns_query_count(self, dag_maker, session):
         """Test that dags_needing_dagruns avoids N+1 on adrq.asset access."""
         num_assets = 10
PATCH

echo "Patch applied successfully."
