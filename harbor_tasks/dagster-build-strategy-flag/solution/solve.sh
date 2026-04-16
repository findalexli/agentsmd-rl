#!/bin/bash
set -e

cd /workspace/dagster

# Idempotency check - verify if patch is already applied
# Check for the distinctive line that the patch adds
if grep -q "build_strategy_option_group = make_option_group" python_modules/libraries/dagster-dg-cli/dagster_dg_cli/cli/plus/deploy/commands.py; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/python_modules/libraries/dagster-dg-cli/dagster_dg_cli/cli/plus/deploy/commands.py b/python_modules/libraries/dagster-dg-cli/dagster_dg_cli/cli/plus/deploy/commands.py
index ce229f01c7282..5288a60fc1a04 100644
--- a/python_modules/libraries/dagster-dg-cli/dagster_dg_cli/cli/plus/deploy/commands.py
+++ b/python_modules/libraries/dagster-dg-cli/dagster_dg_cli/cli/plus/deploy/commands.py
@@ -92,8 +92,29 @@ def _get_deployment(input_deployment: Optional[str], plus_config: DagsterPlusCli
 )


+build_strategy_option_group = make_option_group(
+    {
+        not_none(option.name): option
+        for option in [
+            click.Option(
+                ["--build-strategy"],
+                type=click.Choice(["docker", "python-executable"]),
+                default="docker",
+                help=(
+                    "Build strategy used to build code locations. 'docker' builds a Docker image "
+                    "(required for Hybrid agents). 'python-executable' builds PEX files "
+                    "(Serverless agents only)."
+                ),
+                envvar="DAGSTER_BUILD_STRATEGY",
+            ),
+        ]
+    }
+)
+
+
 @click.group(name="deploy", cls=DgClickGroup, invoke_without_command=True)
 @org_and_deploy_option_group
+@build_strategy_option_group
 @click.option(
     "--python-version",
     "python_version",
@@ -154,6 +175,7 @@ def _get_deployment(input_deployment: Optional[str], plus_config: DagsterPlusCli
 def deploy_group(
     organization: Optional[str],
     deployment: Optional[str],
+    build_strategy: str,
     python_version: Optional[str],
     agent_type_str: str,
     deployment_type_str: Optional[str],
@@ -178,6 +200,8 @@ def deploy_group(
     Each of the individual stages of the deploy is also available as its own subcommand for additional
     customization.
     """
+    from dagster_cloud_cli.commands.ci import BuildStrategy
+
     if click.get_current_context().invoked_subcommand:
         return

@@ -212,6 +236,8 @@ def deploy_group(
     else:
         agent_type = get_agent_type(plus_config)

+    build_strategy_enum = BuildStrategy(build_strategy)
+
     init_deploy_session(
         organization,
         deployment,
@@ -231,6 +257,7 @@ def deploy_group(
     build_artifact(
         dg_context,
         agent_type,
+        build_strategy_enum,
         statedir,
         bool(use_editable_dagster),
         python_version,
@@ -368,6 +395,7 @@ def start_deploy_session_command(
     type=click.Choice([agent_type.value.lower() for agent_type in DgPlusAgentType]),
     help="Whether this a Hybrid or serverless code location.",
 )
+@build_strategy_option_group
 @click.option(
     "--python-version",
     "python_version",
@@ -389,6 +417,7 @@ def start_deploy_session_command(
 @cli_telemetry_wrapper
 def build_and_push_command(
     agent_type_str: str,
+    build_strategy: str,
     python_version: Optional[str],
     use_editable_dagster: Optional[str],
     location_names: tuple[str],
@@ -398,6 +427,8 @@ def build_and_push_command(
     """Builds a Docker image to be deployed, and pushes it to the registry
     that was configured when the deploy session was started.
     """
+    from dagster_cloud_cli.commands.ci import BuildStrategy
+
     cli_config = normalize_cli_config(global_options, click.get_current_context())

     dg_context = DgContext.for_workspace_or_project_environment(target_path, cli_config)
@@ -410,11 +441,14 @@ def build_and_push_command(
         plus_config = DagsterPlusCliConfig.get()
         agent_type = get_agent_type(plus_config)

+    build_strategy_enum = BuildStrategy(build_strategy)
+
     statedir = _get_statedir()

     build_artifact(
         dg_context,
         agent_type,
+        build_strategy_enum,
         statedir,
         bool(use_editable_dagster),
         python_version,
diff --git a/python_modules/libraries/dagster-dg-cli/dagster_dg_cli/cli/plus/deploy/deploy_session.py b/python_modules/libraries/dagster-dg-cli/dagster_dg_cli/cli/plus/deploy/deploy_session.py
index 7b105fec3bf5e..c548c09c89ad3 100644
--- a/python_modules/libraries/dagster-dg-cli/dagster_dg_cli/cli/plus/deploy/deploy_session.py
+++ b/python_modules/libraries/dagster-dg-cli/dagster_dg_cli/cli/plus/deploy/deploy_session.py
@@ -7,10 +7,6 @@
 from typing import TYPE_CHECKING, Optional

 import click
-
-if TYPE_CHECKING:
-    from dagster_cloud_cli.types import SnapshotBaseDeploymentCondition
-
 import dagster_shared.check as check

 # Expensive imports moved to lazy loading inside functions to improve CLI startup performance
@@ -22,6 +18,10 @@
 from dagster_dg_cli.cli.utils import create_temp_dagster_cloud_yaml_file
 from dagster_dg_cli.utils.plus.build import create_deploy_dockerfile, get_dockerfile_path

+if TYPE_CHECKING:
+    from dagster_cloud_cli.commands.ci import BuildStrategy
+    from dagster_cloud_cli.types import SnapshotBaseDeploymentCondition
+

 def _guess_deployment_type(
     project_dir: Path, full_deployment_name: str
@@ -176,20 +176,31 @@ def init_deploy_session(
 def build_artifact(
     dg_context: DgContext,
     agent_type: DgPlusAgentType,
+    build_strategy: "BuildStrategy",
     statedir: str,
     use_editable_dagster: bool,
     python_version: Optional[str],
     location_names: tuple[str],
 ):
+    from dagster_cloud_cli.commands.ci import BuildStrategy
+
     if not python_version:
         python_version = f"3.{sys.version_info.minor}"

+    # Validate build strategy compatibility with agent type
+    if agent_type == DgPlusAgentType.HYBRID and build_strategy == BuildStrategy.pex:
+        raise click.UsageError(
+            "Build strategy 'python-executable' is not supported for Hybrid agents. "
+            "Hybrid agents require 'docker' build strategy."
+        )
+
     requested_location_names = set(location_names)

     if dg_context.is_project:
         _build_artifact_for_project(
             dg_context,
             agent_type,
+            build_strategy,
             statedir,
             use_editable_dagster,
             python_version,
@@ -210,6 +221,7 @@ def build_artifact(
             _build_artifact_for_project(
                 project_context,
                 agent_type,
+                build_strategy,
                 statedir,
                 use_editable_dagster,
                 python_version,
@@ -220,6 +232,7 @@ def build_artifact(
 def _build_artifact_for_project(
     dg_context: DgContext,
     agent_type: DgPlusAgentType,
+    build_strategy: "BuildStrategy",
     statedir: str,
     use_editable_dagster: bool,
     python_version: str,
@@ -256,9 +269,9 @@ def _build_artifact_for_project(
         )

     else:
-        # Import BuildStrategy and deps locally since they're not needed for tests
+        # Import deps locally since they're not needed for tests
         # Lazy import for test mocking and performance
-        from dagster_cloud_cli.commands.ci import BuildStrategy, build_impl
+        from dagster_cloud_cli.commands.ci import build_impl
         from dagster_cloud_cli.core.pex_builder import deps

         build_impl(
@@ -267,7 +280,7 @@ def _build_artifact_for_project(
             use_editable_dagster=use_editable_dagster,
             location_name=[dg_context.code_location_name],
             build_directory=str(build_directory),
-            build_strategy=BuildStrategy.docker,
+            build_strategy=build_strategy,
             docker_image_tag=None,
             docker_base_image=None,
             docker_env=[],
PATCH

echo "Patch applied successfully"
