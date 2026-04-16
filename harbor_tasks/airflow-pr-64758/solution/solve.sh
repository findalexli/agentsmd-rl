#!/bin/bash
# Gold solution for airflow-dag-startdate-tz-overflow
# Applies the fix from apache/airflow#64758

set -e
cd /workspace/airflow

# Idempotency check - skip if already applied
if grep -q "datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)" \
    airflow-core/src/airflow/example_dags/example_inlet_event_extra.py; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/airflow-core/src/airflow/example_dags/example_inlet_event_extra.py b/airflow-core/src/airflow/example_dags/example_inlet_event_extra.py
index ead4b442b782e..eb61ed443f6b2 100644
--- a/airflow-core/src/airflow/example_dags/example_inlet_event_extra.py
+++ b/airflow-core/src/airflow/example_dags/example_inlet_event_extra.py
@@ -33,7 +33,7 @@
 with DAG(
     dag_id="read_asset_event",
     catchup=False,
-    start_date=datetime.datetime.min,
+    start_date=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
     schedule="@daily",
     tags=["consumes"],
 ):
@@ -48,7 +48,7 @@ def read_asset_event(*, inlet_events=None):
 with DAG(
     dag_id="read_asset_event_from_classic",
     catchup=False,
-    start_date=datetime.datetime.min,
+    start_date=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
     schedule="@daily",
     tags=["consumes"],
 ):
diff --git a/airflow-core/src/airflow/example_dags/example_outlet_event_extra.py b/airflow-core/src/airflow/example_dags/example_outlet_event_extra.py
index 04e88554d16d3..7baab90625ded 100644
--- a/airflow-core/src/airflow/example_dags/example_outlet_event_extra.py
+++ b/airflow-core/src/airflow/example_dags/example_outlet_event_extra.py
@@ -33,7 +33,7 @@
 with DAG(
     dag_id="asset_with_extra_by_yield",
     catchup=False,
-    start_date=datetime.datetime.min,
+    start_date=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
     schedule="@daily",
     tags=["produces"],
 ):
@@ -47,7 +47,7 @@ def asset_with_extra_by_yield():
 with DAG(
     dag_id="asset_with_extra_by_context",
     catchup=False,
-    start_date=datetime.datetime.min,
+    start_date=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
     schedule="@daily",
     tags=["produces"],
 ):
@@ -61,7 +61,7 @@ def asset_with_extra_by_context(*, outlet_events=None):
 with DAG(
     dag_id="asset_with_extra_from_classic_operator",
     catchup=False,
-    start_date=datetime.datetime.min,
+    start_date=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
     schedule="@daily",
     tags=["produces"],
 ):
PATCH

echo "Patch applied successfully."
