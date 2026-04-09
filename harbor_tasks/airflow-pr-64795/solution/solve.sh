#!/bin/bash
set -e

cd /workspace/airflow

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/airflow-ctl-tests/tests/airflowctl_tests/test_airflowctl_commands.py b/airflow-ctl-tests/tests/airflowctl_tests/test_airflowctl_commands.py
index 4aea60dca681e..c004f5ccfdb2f 100644
--- a/airflow-ctl-tests/tests/airflowctl_tests/test_airflowctl_commands.py
+++ b/airflow-ctl-tests/tests/airflowctl_tests/test_airflowctl_commands.py
@@ -51,6 +51,7 @@ def date_param():
 TEST_COMMANDS = [
     # Auth commands
     f"auth token {CREDENTIAL_SUFFIX}",
+    "auth list-envs",
     # Assets commands
     "assets list",
     "assets get --asset-id=1",
@@ -168,9 +169,7 @@ def test_hardcoded_xcom_key_would_collide():
 )
 def test_airflowctl_commands(command: str, run_command):
     """Test airflowctl commands using docker-compose environment."""
-    env_vars = {"AIRFLOW_CLI_DEBUG_MODE": "true"}
-
-    run_command(command, env_vars, skip_login=True)
+    run_command(command=command, env_vars={"AIRFLOW_CLI_DEBUG_MODE": "true"}, skip_login=True)


 @pytest.mark.parametrize(
@@ -180,9 +179,12 @@ def test_airflowctl_commands(command: str, run_command):
 )
 def test_airflowctl_commands_skip_keyring(command: str, api_token: str, run_command):
     """Test airflowctl commands using docker-compose environment without using keyring."""
-    env_vars = {}
-    env_vars["AIRFLOW_CLI_TOKEN"] = api_token
-    env_vars["AIRFLOW_CLI_DEBUG_MODE"] = "false"
-    env_vars["AIRFLOW_CLI_ENVIRONMENT"] = "nokeyring"
-
-    run_command(command, env_vars, skip_login=True)
+    run_command(
+        command=command,
+        env_vars={
+            "AIRFLOW_CLI_TOKEN": api_token,
+            "AIRFLOW_CLI_DEBUG_MODE": "false",
+            "AIRFLOW_CLI_ENVIRONMENT": "nokeyring",
+        },
+        skip_login=True,
+    )
PATCH

echo "Patch applied successfully"
