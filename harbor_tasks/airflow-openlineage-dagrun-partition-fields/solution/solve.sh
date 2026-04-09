#!/bin/bash
set -e

cd /workspace/airflow

# Apply the gold patch to add partition_key and partition_date to DagRunInfo
patch -p1 <<'PATCH'
diff --git a/providers/openlineage/src/airflow/providers/openlineage/utils/utils.py b/providers/openlineage/src/airflow/providers/openlineage/utils/utils.py
index 9fb572d628cde..5f11b186b62c7 100644
--- a/providers/openlineage/src/airflow/providers/openlineage/utils/utils.py
+++ b/providers/openlineage/src/airflow/providers/openlineage/utils/utils.py
@@ -744,6 +744,8 @@ class DagRunInfo(InfoJsonEncodable):
         "execution_date",  # Airflow 2
         "external_trigger",  # Removed in Airflow 3, use run_type instead
         "logical_date",  # Airflow 3
+        "partition_key",  # Airflow 3.2+
+        "partition_date",  # Airflow 3.2+
         "run_after",  # Airflow 3
         "run_id",
         "run_type",
diff --git a/providers/openlineage/tests/unit/openlineage/utils/test_utils.py b/providers/openlineage/tests/unit/openlineage/utils/test_utils.py
index 75365cd5a7c09..c406938196196 100644
--- a/providers/openlineage/tests/unit/openlineage/utils/test_utils.py
+++ b/providers/openlineage/tests/unit/openlineage/utils/test_utils.py
@@ -190,6 +190,8 @@ def test_get_airflow_dag_run_facet():
     dagrun_mock.triggering_user_name = "user1"
     dagrun_mock.triggered_by = "something"
     dagrun_mock.note = "note"
+    dagrun_mock.partition_key = "some_partition_key"
+    dagrun_mock.partition_date = datetime.datetime(2024, 6, 1, 2, 3, 34, tzinfo=datetime.timezone.utc)
     dagrun_mock.dag_versions = [
         MagicMock(
             bundle_name="bundle_name",
@@ -242,6 +244,8 @@ def test_get_airflow_dag_run_facet():
                 "dag_version_id": "version_id",
                 "dag_version_number": "version_number",
                 "triggering_user_name": "user1",
+                "partition_key": "some_partition_key",
+                "partition_date": "2024-06-01T02:03:34+00:00",
                 "triggered_by": "something",
                 "note": note,
             },
@@ -2893,6 +2897,8 @@ def test_dagrun_info_af3(mocked_dag_versions):
     optional_args = {}
     if AIRFLOW_V_3_2_PLUS:
         optional_args["note"] = "note"
+        optional_args["partition_key"] = "some_partition_key"
+        optional_args["partition_date"] = date

     mocked_dag_versions.return_value = [dv1, dv2]
     dagrun = DagRun(
@@ -2916,6 +2922,11 @@ def test_dagrun_info_af3(mocked_dag_versions):
     dagrun.end_date = date + datetime.timedelta(seconds=74, microseconds=546)
     dagrun.triggering_user_name = "my_user"

+    optional_result = {}
+    if AIRFLOW_V_3_2_PLUS:
+        optional_result["partition_key"] = "some_partition_key"
+        optional_result["partition_date"] = "2024-06-01T00:00:00+00:00"
+
     result = DagRunInfo(dagrun)
     assert dict(result) == {
         "conf": {"a": 1},
@@ -2938,6 +2949,7 @@ def test_dagrun_info_af3(mocked_dag_versions):
         "triggered_by": DagRunTriggeredByType.UI,
         "triggering_user_name": "my_user",
         "note": optional_args.get("note"),
+        **optional_result,
     }
PATCH

# Verify the patch was applied by checking for the distinctive line
if ! grep -q '"partition_key",  # Airflow 3.2+' providers/openlineage/src/airflow/providers/openlineage/utils/utils.py; then
    echo "ERROR: Patch was not applied successfully"
    exit 1
fi

echo "Patch applied successfully"
