#!/bin/bash
set -e

cd /workspace/airflow

# Apply the patch for OpenLineage injection in EmrServerlessStartJobOperator
git apply <<'PATCH'
diff --git a/providers/amazon/src/airflow/providers/amazon/aws/operators/emr.py b/providers/amazon/src/airflow/providers/amazon/aws/operators/emr.py
index 313cc6494899e..8efc71289e457 100644
--- a/providers/amazon/src/airflow/providers/amazon/aws/operators/emr.py
+++ b/providers/amazon/src/airflow/providers/amazon/aws/operators/emr.py
@@ -58,6 +58,10 @@
 )
 from airflow.providers.amazon.aws.utils.waiter_with_logging import wait
 from airflow.providers.amazon.aws.version_compat import NOTSET, ArgNotSet
+from airflow.providers.common.compat.openlineage.utils.spark import (
+    inject_parent_job_information_into_emr_serverless_properties,
+    inject_transport_information_into_emr_serverless_properties,
+)
 from airflow.providers.common.compat.sdk import AirflowException, conf
 from airflow.utils.helpers import exactly_one, prune_dict

@@ -1197,6 +1201,14 @@ class EmrServerlessStartJobOperator(AwsBaseOperator[EmrServerlessHook]):
     :param cancel_on_kill: If True, the EMR Serverless job will be cancelled when the task is killed
         while in deferrable mode. This ensures that orphan jobs are not left running in EMR Serverless
         when an Airflow task is cancelled. Defaults to True.
+    :param openlineage_inject_parent_job_info: If True, injects OpenLineage parent job information
+        into the EMR Serverless ``spark-defaults`` configuration so the Spark job emits a
+        ``parentRunFacet`` linking back to the Airflow task. Defaults to the
+        ``openlineage.spark_inject_parent_job_info`` config value.
+    :param openlineage_inject_transport_info: If True, injects OpenLineage transport configuration
+        into the EMR Serverless ``spark-defaults`` configuration so the Spark job sends OL events
+        to the same backend as Airflow. Defaults to the
+        ``openlineage.spark_inject_transport_info`` config value.
     """

     aws_hook_class = EmrServerlessHook
@@ -1236,6 +1248,12 @@ def __init__(
         deferrable: bool = conf.getboolean("operators", "default_deferrable", fallback=False),
         enable_application_ui_links: bool = False,
         cancel_on_kill: bool = True,
+        openlineage_inject_parent_job_info: bool = conf.getboolean(
+            "openlineage", "spark_inject_parent_job_info", fallback=False
+        ),
+        openlineage_inject_transport_info: bool = conf.getboolean(
+            "openlineage", "spark_inject_transport_info", fallback=False
+        ),
         **kwargs,
     ):
         waiter_delay = 60 if waiter_delay is NOTSET else waiter_delay
@@ -1254,6 +1272,8 @@ def __init__(
         self.deferrable = deferrable
         self.enable_application_ui_links = enable_application_ui_links
         self.cancel_on_kill = cancel_on_kill
+        self.openlineage_inject_parent_job_info = openlineage_inject_parent_job_info
+        self.openlineage_inject_transport_info = openlineage_inject_transport_info
         super().__init__(**kwargs)

         self.client_request_token = client_request_token or str(uuid4())
@@ -1287,6 +1307,19 @@ def execute(self, context: Context, event: dict[str, Any] | None = None) -> str
             )
         self.log.info("Starting job on Application: %s", self.application_id)
         self.name = self.name or self.config.pop("name", f"emr_serverless_job_airflow_{uuid4()")
+
+        configuration_overrides = self.configuration_overrides
+        if self.openlineage_inject_parent_job_info:
+            self.log.info("Injecting OpenLineage parent job information into EMR Serverless configuration.")
+            configuration_overrides = inject_parent_job_information_into_emr_serverless_properties(
+                configuration_overrides, context
+            )
+        if self.openlineage_inject_transport_info:
+            self.log.info("Injecting OpenLineage transport information into EMR Serverless configuration.")
+            configuration_overrides = inject_transport_information_into_emr_serverless_properties(
+                configuration_overrides, context
+            )
+
         args = {
             "clientToken": self.client_request_token,
             "applicationId": self.application_id,
@@ -1295,8 +1328,8 @@ def execute(self, context: Context, event: dict[str, Any] | None = None) -> str
             "name": self.name,
             **self.config,
         }
-        if self.configuration_overrides is not None:
-            args["configurationOverrides"] = self.configuration_overrides
+        if configuration_overrides is not None:
+            args["configurationOverrides"] = configuration_overrides
         response = self.hook.conn.start_job_run(
             **args,
         )
diff --git a/providers/common/compat/src/airflow/providers/common/compat/openlineage/utils/spark.py b/providers/common/compat/src/airflow/providers/common/compat/openlineage/utils/spark.py
index d92dad56dad8f..91b4fae05d50a 100644
--- a/providers/common/compat/src/airflow/providers/common/compat/openlineage/utils/spark.py
+++ b/providers/common/compat/src/airflow/providers/common/compat/openlineage/utils/spark.py
@@ -24,16 +24,20 @@

 if TYPE_CHECKING:
     from airflow.providers.openlineage.utils.spark import (
+        inject_parent_job_information_into_emr_serverless_properties,
         inject_parent_job_information_into_glue_arguments,
         inject_parent_job_information_into_spark_properties,
+        inject_transport_information_into_emr_serverless_properties,
         inject_transport_information_into_glue_arguments,
         inject_transport_information_into_spark_properties,
     )
     from airflow.sdk import Context
 try:
     from airflow.providers.openlineage.utils.spark import (
+        inject_parent_job_information_into_emr_serverless_properties,
         inject_parent_job_information_into_glue_arguments,
         inject_parent_job_information_into_spark_properties,
+        inject_transport_information_into_emr_serverless_properties,
         inject_transport_information_into_glue_arguments,
         inject_transport_information_into_spark_properties,
     )
@@ -67,10 +71,32 @@ def inject_transport_information_into_glue_arguments(script_args: dict, context:
         )
         return script_args

+    def inject_parent_job_information_into_emr_serverless_properties(
+        configuration_overrides: dict | None, context: Context
+    ) -> dict:
+        log.warning(
+            "Could not import `airflow.providers.openlineage.plugins.macros`."
+            "Skipping the injection of OpenLineage parent job information into "
+            "EMR Serverless configuration."
+        )
+        return configuration_overrides or {}
+
+    def inject_transport_information_into_emr_serverless_properties(
+        configuration_overrides: dict | None, context: Context
+    ) -> dict:
+        log.warning(
+            "Could not import `airflow.providers.openlineage.plugins.listener`."
+            "Skipping the injection of OpenLineage transport information into "
+            "EMR Serverless configuration."
+        )
+        return configuration_overrides or {}
+

 __all__ = [
+    "inject_parent_job_information_into_emr_serverless_properties",
     "inject_parent_job_information_into_glue_arguments",
     "inject_parent_job_information_into_spark_properties",
+    "inject_transport_information_into_emr_serverless_properties",
     "inject_transport_information_into_glue_arguments",
     "inject_transport_information_into_spark_properties",
 ]
diff --git a/providers/openlineage/src/airflow/providers/openlineage/utils/spark.py b/providers/openlineage/src/airflow/providers/openlineage/utils/spark.py
index 837946fecbefd..4b67d9383d033 100644
--- a/providers/openlineage/src/airflow/providers/openlineage/utils/spark.py
+++ b/providers/openlineage/src/airflow/providers/openlineage/utils/spark.py
@@ -265,3 +265,93 @@ def inject_transport_information_into_glue_arguments(script_args: dict, context:

     combined_conf = f"{existing_conf} --conf {new_conf_parts}" if existing_conf else new_conf_parts
     return {**script_args, "--conf": combined_conf}
+
+
+def _get_or_create_spark_defaults_properties(configuration_overrides: dict) -> dict:
+    """
+    Find or create the ``spark-defaults`` classification entry and return its ``properties`` dict.
+
+    The ``configuration_overrides`` structure for EMR Serverless is::
+
+        {"applicationConfiguration": [{"classification": "spark-defaults", "properties": {...}}, ...]}
+
+    If no ``spark-defaults`` entry exists, one is created.
+    """
+    app_config = configuration_overrides.setdefault("applicationConfiguration", [])
+    for entry in app_config:
+        if entry.get("classification") == "spark-defaults":
+            entry.setdefault("properties", {})
+            return entry["properties"]
+    new_entry: dict = {"classification": "spark-defaults", "properties": {}}
+    app_config.append(new_entry)
+    return new_entry["properties"]
+
+
+def inject_parent_job_information_into_emr_serverless_properties(
+    configuration_overrides: dict | None, context: Context
+) -> dict:
+    """
+    Inject parent job information into EMR Serverless configuration if not already present.
+
+    EMR Serverless passes Spark properties via a nested ``applicationConfiguration``
+    structure with ``classification: spark-defaults``.
+
+    Args:
+        configuration_overrides: EMR Serverless configuration overrides dict (may be None).
+        context: The context containing task instance information.
+
+    Returns:
+        Modified configuration_overrides dict with OpenLineage parent job information injected.
+    """
+    import copy
+
+    result = copy.deepcopy(configuration_overrides) if configuration_overrides else {}
+    properties = _get_or_create_spark_defaults_properties(result)
+
+    if _is_parent_job_information_present_in_spark_properties(properties):
+        log.info(
+            "Some OpenLineage properties with parent job information are already present "
+            "in EMR Serverless Spark properties. Skipping the injection of OpenLineage "
+            "parent job information into EMR Serverless configuration."
+        )
+        return result
+
+    parent_props = _get_parent_job_information_as_spark_properties(context)
+    if parent_props:
+        properties.update(parent_props)
+    return result
+
+
+def inject_transport_information_into_emr_serverless_properties(
+    configuration_overrides: dict | None, context: Context
+) -> dict:
+    """
+    Inject transport information into EMR Serverless configuration if not already present.
+
+    EMR Serverless passes Spark properties via a nested ``applicationConfiguration``
+    structure with ``classification: spark-defaults``.
+
+    Args:
+        configuration_overrides: EMR Serverless configuration overrides dict (may be None).
+        context: The context containing task instance information.
+
+    Returns:
+        Modified configuration_overrides dict with OpenLineage transport information injected.
+    """
+    import copy
+
+    result = copy.deepcopy(configuration_overrides) if configuration_overrides else {}
+    properties = _get_or_create_spark_defaults_properties(result)
+
+    if _is_transport_information_present_in_spark_properties(properties):
+        log.info(
+            "Some OpenLineage properties with transport information are already present "
+            "in EMR Serverless Spark properties. Skipping the injection of OpenLineage "
+            "transport information into EMR Serverless configuration."
+        )
+        return result
+
+    transport_props = _get_transport_information_as_spark_properties()
+    if transport_props:
+        properties.update(transport_props)
+    return result
PATCH

echo "Patch applied successfully"
