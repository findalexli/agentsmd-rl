#!/bin/bash
set -e

cd /workspace/dagster

# Apply the gold patch
git apply <<'PATCH'
diff --git a/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py b/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py
index faf5b20f47899..3e68b49709eb8 100644
--- a/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py
+++ b/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py
@@ -282,6 +282,18 @@ def _run(
                 ]
             )

+        # Dlt keeps some local state that interferes with next runs.
+        # This is annoying when an asset fails and running a different one on the same pipeline
+        # would just pick up the failing job and fail again.
+        # When restore_from_destination is enabled (default), we can safely drop all local state
+        # because it will be restored from the destination.
+        # When restore_from_destination is disabled, we only drop pending packages to avoid
+        # wiping incremental loading cursors that can't be recovered from the destination.
+        if dlt_pipeline.config.restore_from_destination:
+            dlt_pipeline.drop()
+        else:
+            dlt_pipeline.drop_pending_packages()
+
         load_info = dlt_pipeline.run(dlt_source, **kwargs)

         load_info.raise_on_failed_jobs()
diff --git a/python_modules/libraries/dagster-dlt/dagster_dlt_tests/test_asset_decorator.py b/python_modules/libraries/dagster-dlt/dagster_dlt_tests/test_asset_decorator.py
index 16e5826a9c5f6..1734f797e1360 100644
--- a/python_modules/libraries/dagster-dlt/dagster_dlt_tests/test_asset_decorator.py
+++ b/python_modules/libraries/dagster-dlt/dagster_dlt_tests/test_asset_decorator.py
@@ -859,6 +859,68 @@ def my_dlt_assets(dlt_pipeline_resource: DagsterDltResource): ...
     }


+def test_drop_clears_stale_pipeline_state_before_run(dlt_pipeline: Pipeline) -> None:
+    # First run to populate the destination so it's not empty.
+    # This sets first_run=False and _state_restored=True internally.
+    dlt_pipeline.run(pipeline())
+
+    @dlt.source
+    def stale_source():
+        @dlt.resource
+        def stale_data():
+            yield {"id": 1, "value": "stale"}
+
+        return stale_data
+
+    # Create stale normalized packages. Without drop(), dlt.run() would load
+    # these stale packages and return early, never processing the real source.
+    dlt_pipeline.extract(stale_source())
+    dlt_pipeline.normalize()
+
+    @dlt_assets(dlt_source=pipeline(), dlt_pipeline=dlt_pipeline)
+    def example_pipeline_assets(
+        context: AssetExecutionContext, dlt_pipeline_resource: DagsterDltResource
+    ):
+        yield from dlt_pipeline_resource.run(context=context)
+
+    res = materialize(
+        [example_pipeline_assets],
+        resources={"dlt_pipeline_resource": DagsterDltResource()},
+    )
+    assert res.success
+
+
+def test_drop_pending_packages_when_restore_from_destination_disabled(
+    dlt_pipeline: Pipeline,
+) -> None:
+    @dlt.source
+    def stale_source():
+        @dlt.resource
+        def stale_data():
+            yield {"id": 1, "value": "stale"}
+
+        return stale_data
+
+    dlt_pipeline.config.restore_from_destination = False
+
+    # Create stale extracted and normalized packages without loading.
+    # This simulates a previous run that failed after normalization.
+    dlt_pipeline.extract(stale_source())
+    dlt_pipeline.normalize()
+
+    @dlt_assets(dlt_source=pipeline(), dlt_pipeline=dlt_pipeline)
+    def example_pipeline_assets(
+        context: AssetExecutionContext, dlt_pipeline_resource: DagsterDltResource
+    ):
+        yield from dlt_pipeline_resource.run(context=context)
+
+    res = materialize(
+        [example_pipeline_assets],
+        resources={"dlt_pipeline_resource": DagsterDltResource()},
+    )
+    assert res.success
+
+
 def test_translator_invariant_group_name_with_asset_decorator(dlt_pipeline: Pipeline) -> None:
     class CustomDagsterDltTranslator(DagsterDltTranslator):
         def get_asset_spec(self, data: DltResourceTranslatorData) -> AssetSpec:
PATCH