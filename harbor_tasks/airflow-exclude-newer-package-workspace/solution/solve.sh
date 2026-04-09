#!/bin/bash
set -e

cd /workspace/airflow

# Apply the gold patch for PR #64859
patch -p1 << 'PATCH'
diff --git a/pyproject.toml b/pyproject.toml
index 19ec74e0df6dd..5e9600bbbfe1b 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -1344,9 +1344,276 @@ leveldb = [

 [tool.uv]
 required-version = ">=0.9.17"
+no-build-isolation-package = ["sphinx-redoc"]
 # Synchroonize with scripts/ci/prek/upgrade_important_versions.py
 exclude-newer = "4 days"
-no-build-isolation-package = ["sphinx-redoc"]
+
+[tool.uv.exclude-newer-package]
+# Automatically generated exclude-newer-package entries (update_airflow_pyproject_toml.py)
+apache-airflow = false
+apache-airflow-breeze = false
+apache-airflow-core = false
+apache-airflow-ctl = false
+apache-airflow-ctl-tests = false
+apache-airflow-dev = false
+apache-airflow-devel-common = false
+apache-airflow-docker-tests = false
+apache-airflow-e2e-tests = false
+apache-airflow-helm-tests = false
+apache-airflow-kubernetes-tests = false
+apache-airflow-providers = false
+apache-airflow-providers-airbyte = false
+apache-airflow-providers-alibaba = false
+apache-airflow-providers-amazon = false
+apache-airflow-providers-apache-cassandra = false
+apache-airflow-providers-apache-drill = false
+apache-airflow-providers-apache-druid = false
+apache-airflow-providers-apache-flink = false
+apache-airflow-providers-apache-hdfs = false
+apache-airflow-providers-apache-hive = false
+apache-airflow-providers-apache-iceberg = false
+apache-airflow-providers-apache-impala = false
+apache-airflow-providers-apache-kafka = false
+apache-airflow-providers-apache-kylin = false
+apache-airflow-providers-apache-livy = false
+apache-airflow-providers-apache-pig = false
+apache-airflow-providers-apache-pinot = false
+apache-airflow-providers-apache-spark = false
+apache-airflow-providers-apache-tinkerpop = false
+apache-airflow-providers-apprise = false
+apache-airflow-providers-arangodb = false
+apache-airflow-providers-asana = false
+apache-airflow-providers-atlassian-jira = false
+apache-airflow-providers-celery = false
+apache-airflow-providers-cloudant = false
+apache-airflow-providers-cncf-kubernetes = false
+apache-airflow-providers-cohere = false
+apache-airflow-providers-common-ai = false
+apache-airflow-providers-common-compat = false
+apache-airflow-providers-common-io = false
+apache-airflow-providers-common-messaging = false
+apache-airflow-providers-common-sql = false
+apache-airflow-providers-databricks = false
+apache-airflow-providers-datadog = false
+apache-airflow-providers-dbt-cloud = false
+apache-airflow-providers-dingding = false
+apache-airflow-providers-discord = false
+apache-airflow-providers-docker = false
+apache-airflow-providers-edge3 = false
+apache-airflow-providers-elasticsearch = false
+apache-airflow-providers-exasol = false
+apache-airflow-providers-fab = false
+apache-airflow-providers-facebook = false
+apache-airflow-providers-ftp = false
+apache-airflow-providers-git = false
+apache-airflow-providers-github = false
+apache-airflow-providers-google = false
+apache-airflow-providers-grpc = false
+apache-airflow-providers-hashicorp = false
+apache-airflow-providers-http = false
+apache-airflow-providers-imap = false
+apache-airflow-providers-influxdb = false
+apache-airflow-providers-informatica = false
+apache-airflow-providers-jdbc = false
+apache-airflow-providers-jenkins = false
+apache-airflow-providers-keycloak = false
+apache-airflow-providers-microsoft-azure = false
+apache-airflow-providers-microsoft-mssql = false
+apache-airflow-providers-microsoft-psrp = false
+apache-airflow-providers-microsoft-winrm = false
+apache-airflow-providers-mongo = false
+apache-airflow-providers-mysql = false
+apache-airflow-providers-neo4j = false
+apache-airflow-providers-odbc = false
+apache-airflow-providers-openai = false
+apache-airflow-providers-openfaas = false
+apache-airflow-providers-openlineage = false
+apache-airflow-providers-opensearch = false
+apache-airflow-providers-opsgenie = false
+apache-airflow-providers-oracle = false
+apache-airflow-providers-pagerduty = false
+apache-airflow-providers-papermill = false
+apache-airflow-providers-pgvector = false
+apache-airflow-providers-pinecone = false
+apache-airflow-providers-postgres = false
+apache-airflow-providers-presto = false
+apache-airflow-providers-qdrant = false
+apache-airflow-providers-redis = false
+apache-airflow-providers-salesforce = false
+apache-airflow-providers-samba = false
+apache-airflow-providers-segment = false
+apache-airflow-providers-sendgrid = false
+apache-airflow-providers-sftp = false
+apache-airflow-providers-singularity = false
+apache-airflow-providers-slack = false
+apache-airflow-providers-smtp = false
+apache-airflow-providers-snowflake = false
+apache-airflow-providers-sqlite = false
+apache-airflow-providers-ssh = false
+apache-airflow-providers-standard = false
+apache-airflow-providers-tableau = false
+apache-airflow-providers-telegram = false
+apache-airflow-providers-teradata = false
+apache-airflow-providers-trino = false
+apache-airflow-providers-vertica = false
+apache-airflow-providers-weaviate = false
+apache-airflow-providers-yandex = false
+apache-airflow-providers-ydb = false
+apache-airflow-providers-zendesk = false
+apache-airflow-scripts = false
+apache-airflow-shared-configuration = false
+apache-airflow-shared-dagnode = false
+apache-airflow-shared-listeners = false
+apache-airflow-shared-logging = false
+apache-airflow-shared-module-loading = false
+apache-airflow-shared-observability = false
+apache-airflow-shared-plugins-manager = false
+apache-airflow-shared-providers-discovery = false
+apache-airflow-shared-secrets-backend = false
+apache-airflow-shared-secrets-masker = false
+apache-airflow-shared-serialization = false
+apache-airflow-shared-template-rendering = false
+apache-airflow-shared-timezones = false
+apache-airflow-task-sdk = false
+apache-airflow-task-sdk-integration-tests = false
+apache-aurflow-docker-stack = false
+# End of automatically generated exclude-newer-package entries
+
+[tool.uv.pip]
+# Synchroonize with scripts/ci/prek/upgrade_important_versions.py
+exclude-newer = "4 days"
+
+[tool.uv.pip.exclude-newer-package]
+# Automatically generated exclude-newer-package-pip entries (update_airflow_pyproject_toml.py)
+apache-airflow = false
+apache-airflow-breeze = false
+apache-airflow-core = false
+apache-airflow-ctl = false
+apache-airflow-ctl-tests = false
+apache-airflow-dev = false
+apache-airflow-devel-common = false
+apache-airflow-docker-tests = false
+apache-airflow-e2e-tests = false
+apache-airflow-helm-tests = false
+apache-airflow-kubernetes-tests = false
+apache-airflow-providers = false
+apache-airflow-providers-airbyte = false
+apache-airflow-providers-alibaba = false
+apache-airflow-providers-amazon = false
+apache-airflow-providers-apache-cassandra = false
+apache-airflow-providers-apache-drill = false
+apache-airflow-providers-apache-druid = false
+apache-airflow-providers-apache-flink = false
+apache-airflow-providers-apache-hdfs = false
+apache-airflow-providers-apache-hive = false
+apache-airflow-providers-apache-iceberg = false
+apache-airflow-providers-apache-impala = false
+apache-airflow-providers-apache-kafka = false
+apache-airflow-providers-apache-kylin = false
+apache-airflow-providers-apache-livy = false
+apache-airflow-providers-apache-pig = false
+apache-airflow-providers-apache-pinot = false
+apache-airflow-providers-apache-spark = false
+apache-airflow-providers-apache-tinkerpop = false
+apache-airflow-providers-apprise = false
+apache-airflow-providers-arangodb = false
+apache-airflow-providers-asana = false
+apache-airflow-providers-atlassian-jira = false
+apache-airflow-providers-celery = false
+apache-airflow-providers-cloudant = false
+apache-airflow-providers-cncf-kubernetes = false
+apache-airflow-providers-cohere = false
+apache-airflow-providers-common-ai = false
+apache-airflow-providers-common-compat = false
+apache-airflow-providers-common-io = false
+apache-airflow-providers-common-messaging = false
+apache-airflow-providers-common-sql = false
+apache-airflow-providers-databricks = false
+apache-airflow-providers-datadog = false
+apache-airflow-providers-dbt-cloud = false
+apache-airflow-providers-dingding = false
+apache-airflow-providers-discord = false
+apache-airflow-providers-docker = false
+apache-airflow-providers-edge3 = false
+apache-airflow-providers-elasticsearch = false
+apache-airflow-providers-exasol = false
+apache-airflow-providers-fab = false
+apache-airflow-providers-facebook = false
+apache-airflow-providers-ftp = false
+apache-airflow-providers-git = false
+apache-airflow-providers-github = false
+apache-airflow-providers-google = false
+apache-airflow-providers-grpc = false
+apache-airflow-providers-hashicorp = false
+apache-airflow-providers-http = false
+apache-airflow-providers-imap = false
+apache-airflow-providers-influxdb = false
+apache-airflow-providers-informatica = false
+apache-airflow-providers-jdbc = false
+apache-airflow-providers-jenkins = false
+apache-airflow-providers-keycloak = false
+apache-airflow-providers-microsoft-azure = false
+apache-airflow-providers-microsoft-mssql = false
+apache-airflow-providers-microsoft-psrp = false
+apache-airflow-providers-microsoft-winrm = false
+apache-airflow-providers-mongo = false
+apache-airflow-providers-mysql = false
+apache-airflow-providers-neo4j = false
+apache-airflow-providers-odbc = false
+apache-airflow-providers-openai = false
+apache-airflow-providers-openfaas = false
+apache-airflow-providers-openlineage = false
+apache-airflow-providers-opensearch = false
+apache-airflow-providers-opsgenie = false
+apache-airflow-providers-oracle = false
+apache-airflow-providers-pagerduty = false
+apache-airflow-providers-papermill = false
+apache-airflow-providers-pgvector = false
+apache-airflow-providers-pinecone = false
+apache-airflow-providers-postgres = false
+apache-airflow-providers-presto = false
+apache-airflow-providers-qdrant = false
+apache-airflow-providers-redis = false
+apache-airflow-providers-salesforce = false
+apache-airflow-providers-samba = false
+apache-airflow-providers-segment = false
+apache-airflow-providers-sendgrid = false
+apache-airflow-providers-sftp = false
+apache-airflow-providers-singularity = false
+apache-airflow-providers-slack = false
+apache-airflow-providers-smtp = false
+apache-airflow-providers-snowflake = false
+apache-airflow-providers-sqlite = false
+apache-airflow-providers-ssh = false
+apache-airflow-providers-standard = false
+apache-airflow-providers-tableau = false
+apache-airflow-providers-telegram = false
+apache-airflow-providers-teradata = false
+apache-airflow-providers-trino = false
+apache-airflow-providers-vertica = false
+apache-airflow-providers-weaviate = false
+apache-airflow-providers-yandex = false
+apache-airflow-providers-ydb = false
+apache-airflow-providers-zendesk = false
+apache-airflow-scripts = false
+apache-airflow-shared-configuration = false
+apache-airflow-shared-dagnode = false
+apache-airflow-shared-listeners = false
+apache-airflow-shared-logging = false
+apache-airflow-shared-module-loading = false
+apache-airflow-shared-observability = false
+apache-airflow-shared-plugins-manager = false
+apache-airflow-shared-providers-discovery = false
+apache-airflow-shared-secrets-backend = false
+apache-airflow-shared-secrets-masker = false
+apache-airflow-shared-serialization = false
+apache-airflow-shared-template-rendering = false
+apache-airflow-shared-timezones = false
+apache-airflow-task-sdk = false
+apache-airflow-task-sdk-integration-tests = false
+apache-aurflow-docker-stack = false
+# End of automatically generated exclude-newer-package-pip entries
+

 [tool.uv.sources]
 # These names must match the names as defined in the pyproject.toml of the workspace items,
diff --git a/scripts/ci/docker-compose/remove-sources.yml b/scripts/ci/docker-compose/remove-sources.yml
index bd08c89116b23..a4287f26e46d3 100644
--- a/scripts/ci/docker-compose/remove-sources.yml
+++ b/scripts/ci/docker-compose/remove-sources.yml
@@ -126,8 +126,10 @@ services:
       - ../../../empty:/opt/airflow/providers/ydb/src
       - ../../../empty:/opt/airflow/providers/zendesk/src
       # END automatically generated volumes by generate-volumes-for-sources prek hook
-      # However we keep in_container scripts to be able to debug easily the scripts that
-      # are run with --mount-sources removed flag - such as installing airflow and providers
+      # However we keep in_container scripts and pyproject.toml to be able to debug easily the scripts that
+      # are run with --mount-sources removed flag - such as installing airflow and providers or in order to
+      # get latest uv configuration for all uv sync commands
+      - ../../../pyproject.toml:/opt/airflow/pyproject.toml
       - type: bind
         source: ../../../scripts/in_container
         target: /opt/airflow/scripts/in_container
diff --git a/scripts/ci/prek/update_airflow_pyproject_toml.py b/scripts/ci/prek/update_airflow_pyproject_toml.py
index ff3ee1e1fe244..2143432dedda7 100755
--- a/scripts/ci/prek/update_airflow_pyproject_toml.py
+++ b/scripts/ci/prek/update_airflow_pyproject_toml.py
@@ -67,8 +67,19 @@)
 )
 END_PROVIDER_WORKSPACE_MEMBERS = "    # End of automatically generated provider workspace members"

+START_EXCLUDE_NEWER_PACKAGE = (
+    "# Automatically generated exclude-newer-package entries (update_airflow_pyproject_toml.py)"
+)
+END_EXCLUDE_NEWER_PACKAGE = "# End of automatically generated exclude-newer-package entries"
+
+START_EXCLUDE_NEWER_PACKAGE_PIP = (
+    "# Automatically generated exclude-newer-package-pip entries (update_airflow_pyproject_toml.py)"
+)
+END_EXCLUDE_NEWER_PACKAGE_PIP = "# End of automatically generated exclude-newer-package-pip entries"
+
 CUT_OFF_TIMEDELTA = timedelta(days=6 * 30)

+
 # Temporary override for providers that are not yet included in constraints or when they need
 # minimum versions for compatibility with Airflow 3
 MIN_VERSION_OVERRIDE: dict[str, Version] = {
@@ -116,6 +127,15 @@ def _read_toml(path: Path) -> dict[str, Any]:
     return tomllib.loads(path.read_text())


+def get_all_workspace_component_names() -> list[str]:
+    """Get all workspace component names from [tool.uv.sources] in pyproject.toml."""
+    toml_dict = _read_toml(AIRFLOW_PYPROJECT_TOML_FILE)
+    sources = toml_dict.get("tool", {}).get("uv", {}).get("sources", {})
+    return sorted(
+        name for name, value in sources.items() if isinstance(value, dict) and value.get("workspace")
+    )
+
+
 def get_local_provider_version(provider_id: str) -> Version | None:
     provider_pyproject = PROVIDERS_DIR / provider_id / "pyproject.toml"
     if not provider_pyproject.exists():
@@ -300,3 +320,23 @@ def get_python_exclusion(provider_dependencies: dict[str, Any]) -> str:
         False,
         "provider workspace members",
     )
+    all_workspace_components = get_all_workspace_component_names()
+    exclude_newer_entries = []
+    for component in all_workspace_components:
+        exclude_newer_entries.append(f"{component} = false\n")
+    insert_documentation(
+        AIRFLOW_PYPROJECT_TOML_FILE,
+        exclude_newer_entries,
+        START_EXCLUDE_NEWER_PACKAGE,
+        END_EXCLUDE_NEWER_PACKAGE,
+        False,
+        "exclude-newer-package entries",
+    )
+    insert_documentation(
+        AIRFLOW_PYPROJECT_TOML_FILE,
+        exclude_newer_entries,
+        START_EXCLUDE_NEWER_PACKAGE_PIP,
+        END_EXCLUDE_NEWER_PACKAGE_PIP,
+        False,
+        "exclude-newer-package-pip entries",
+    )
diff --git a/scripts/in_container/install_airflow_and_providers.py b/scripts/in_container/install_airflow_and_providers.py
index 3118773721554..80d7fa601cb64 100755
--- a/scripts/in_container/install_airflow_and_providers.py
+++ b/scripts/in_container/install_airflow_and_providers.py
@@ -23,7 +23,6 @@
 import re
 import shutil
 import sys
-from datetime import datetime
 from functools import cache
 from pathlib import Path
 from typing import NamedTuple
@@ -1129,7 +1128,7 @@ def _install_airflow_and_optionally_providers_together(
     ]
     if installation_spec.pre_release:
         console.print("[bright_blue]Allowing pre-release versions of airflow and providers")
-        base_install_cmd.extend(["--pre", "--exclude-newer", datetime.now().isoformat()])
+        base_install_cmd.extend(["--pre"])
     if installation_spec.airflow_distribution:
         console.print(
             f"\n[bright_blue]Adding airflow distribution to installation: {installation_spec.airflow_distribution} "
@@ -1226,7 +1225,7 @@ def _install_only_airflow_airflow_core_task_sdk_with_constraints(
     ]
     if installation_spec.pre_release:
         console.print("[bright_blue]Allowing pre-release versions of airflow and providers")
-        base_install_airflow_cmd.extend(["--pre", "--exclude-newer", datetime.now().isoformat()])
+        base_install_airflow_cmd.extend(["--pre"])
     if installation_spec.airflow_distribution:
         console.print(
             f"\n[bright_blue]Installing airflow distribution: {installation_spec.airflow_distribution} with constraints"
PATCH

echo "Patch applied successfully"
