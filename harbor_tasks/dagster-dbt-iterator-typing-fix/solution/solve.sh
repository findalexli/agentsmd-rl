#!/bin/bash
set -e

cd /workspace/dagster

# Check if already patched (idempotency)
if grep -q "DbtEventIterator\[DbtDagsterEventType\]" python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the patch
cat <<'PATCH' | git apply -
diff --git a/python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py b/python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py
index 0f983b20f2621..7e4e3dd19f9d3 100644
--- a/python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py
+++ b/python_modules/libraries/dagster-dbt/dagster_dbt/components/dbt_project/component.py
@@ -35,6 +35,7 @@ from dagster_dbt.components.dbt_component_utils import (
     resolve_cli_args,
 )
 from dagster_dbt.components.dbt_project.scaffolder import DbtProjectComponentScaffolder
+from dagster_dbt.core.dbt_event_iterator import DbtDagsterEventType, DbtEventIterator
 from dagster_dbt.core.resource import DbtCliResource
 from dagster_dbt.dagster_dbt_translator import DagsterDbtTranslator, validate_translator
 from dagster_dbt.dbt_manifest import validate_manifest
@@ -383,7 +384,7 @@ class DbtProjectComponent(StateBackedComponent, dg.Resolvable):

     def _get_dbt_event_iterator(
         self, context: dg.AssetExecutionContext, dbt: DbtCliResource
-    ) -> Iterator:
+    ) -> DbtEventIterator[DbtDagsterEventType]:
         iterator = dbt.cli(self.get_cli_args(context), context=context).stream()
         if "column_metadata" in self.include_metadata:
             iterator = iterator.fetch_column_metadata()
diff --git a/python_modules/libraries/dagster-dbt/dagster_dbt/core/dbt_event_iterator.py b/python_modules/libraries/dagster-dbt/dagster_dbt/core/dbt_event_iterator.py
index f9e95e0614db1..a9892349e9406 100644
--- a/python_modules/libraries/dagster-dbt/dagster_dbt/core/dbt_event_iterator.py
+++ b/python_modules/libraries/dagster-dbt/dagster_dbt/core/dbt_event_iterator.py
@@ -220,7 +220,7 @@ class DbtEventIterator(Generic[T]):
     @public
     def fetch_row_counts(
         self,
-    ) -> "DbtEventIterator[Output | AssetMaterialization | AssetCheckResult | AssetObservation | AssetCheckEvaluation]":
+    ) -> "DbtEventIterator[DbtDagsterEventType]":
         """Functionality which will fetch row counts for materialized dbt
         models in a dbt run once they are built. Note that row counts will not be fetched
         for views, since this requires running the view's SQL query which may be costly.
@@ -236,7 +236,7 @@ class DbtEventIterator(Generic[T]):
     def fetch_column_metadata(
         self,
         with_column_lineage: bool = True,
-    ) -> "DbtEventIterator[Output | AssetMaterialization | AssetCheckResult | AssetObservation | AssetCheckEvaluation]":
+    ) -> "DbtEventIterator[DbtDagsterEventType]":
         """Functionality which will fetch column schema metadata for dbt models in a run
         once they're built. It will also fetch schema information for upstream models and generate
         column lineage metadata using sqlglot, if enabled.
@@ -323,7 +323,7 @@ class DbtEventIterator(Generic[T]):
         self,
         skip_config_check: bool = False,
         record_observation_usage: bool = True,
-    ) -> "DbtEventIterator[Output | AssetMaterialization | AssetObservation | AssetCheckResult | AssetCheckEvaluation]":
+    ) -> "DbtEventIterator[DbtDagsterEventType]":
         """Associate each warehouse query with the produced asset materializations for use in Dagster
         Plus Insights. Currently supports Snowflake and BigQuery.
PATCH

echo "Patch applied successfully"
