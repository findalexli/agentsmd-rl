#!/bin/bash
set -e

cd /workspace/airflow

# Apply the fix: Add --exclude-newer to pre-release pip installs
cat <<'PATCH' | git apply -
diff --git a/scripts/in_container/install_airflow_and_providers.py b/scripts/in_container/install_airflow_and_providers.py
index df7443271af3e..3118773721554 100755
--- a/scripts/in_container/install_airflow_and_providers.py
+++ b/scripts/in_container/install_airflow_and_providers.py
@@ -23,6 +23,7 @@
 import re
 import shutil
 import sys
+from datetime import datetime
 from functools import cache
 from pathlib import Path
 from typing import NamedTuple
@@ -1127,7 +1128,8 @@ def _install_airflow_and_optionally_providers_together(
         "install",
     ]
     if installation_spec.pre_release:
-        base_install_cmd.append("--pre")
+        console.print("[bright_blue]Allowing pre-release versions of airflow and providers")
+        base_install_cmd.extend(["--pre", "--exclude-newer", datetime.now().isoformat()])
     if installation_spec.airflow_distribution:
         console.print(
             f"\n[bright_blue]Adding airflow distribution to installation: {installation_spec.airflow_distribution} "
@@ -1223,8 +1225,8 @@ def _install_only_airflow_airflow_core_task_sdk_with_constraints(
         "install",
     ]
     if installation_spec.pre_release:
-        console.print("[bright_blue]Allowing pre-release versions of airflow")
-        base_install_airflow_cmd.append("--pre")
+        console.print("[bright_blue]Allowing pre-release versions of airflow and providers")
+        base_install_airflow_cmd.extend(["--pre", "--exclude-newer", datetime.now().isoformat()])
     if installation_spec.airflow_distribution:
         console.print(
             f"\n[bright_blue]Installing airflow distribution: {installation_spec.airflow_distribution} with constraints"
PATCH

# Verify the patch was applied (idempotency check)
if ! grep -q "from datetime import datetime" scripts/in_container/install_airflow_and_providers.py; then
    echo "ERROR: Failed to apply patch - datetime import not found"
    exit 1
fi

if ! grep -q "exclude-newer" scripts/in_container/install_airflow_and_providers.py; then
    echo "ERROR: Failed to apply patch - exclude-newer not found"
    exit 1
fi

echo "Patch applied successfully"
