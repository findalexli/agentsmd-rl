#!/bin/bash
set -e

cd /workspace/airflow

# Idempotency check - skip if patch already applied
if grep -q "def get_dependency_groups" scripts/tools/initialize_virtualenv.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/scripts/tools/initialize_virtualenv.py b/scripts/tools/initialize_virtualenv.py
index 7bc754c43ad33..fff6fbb4b6227 100755
--- a/scripts/tools/initialize_virtualenv.py
+++ b/scripts/tools/initialize_virtualenv.py
@@ -55,7 +55,19 @@ def check_for_package_extras() -> str:
     return "dev"


-def uv_install_requirements() -> int:
+def get_dependency_groups(pyproject_toml_path: Path) -> list[str]:
+    """
+    Get the dependency groups from pyproject.toml
+    """
+    try:
+        import tomllib
+    except ImportError:
+        import tomli as tomllib
+    airflow_core_toml_dict = tomllib.loads(pyproject_toml_path.read_text())
+    return airflow_core_toml_dict["dependency-groups"].keys()
+
+
+def uv_install_requirements(airflow_pyproject_toml_file: Path) -> int:
     """
     install the requirements of the current python version.
     return 0 if success, anything else is an error.
@@ -87,7 +99,12 @@ def uv_install_requirements() -> int:

 """
     )
-    extra_param = [x for extra in extras.split(",") for x in ("--group", extra)]
+    dependency_groups = get_dependency_groups(airflow_pyproject_toml_file)
+    extra_param = [
+        flag
+        for extra in extras.split(",")
+        for flag in (["--group", extra] if extra in dependency_groups else ["--extra", extra])
+    ]
     uv_install_command = ["uv", "sync"] + extra_param
     quoted_command = " ".join([shlex.quote(parameter) for parameter in uv_install_command])
     print()
@@ -139,7 +156,8 @@ def main():

     clean_up_airflow_home(airflow_home_dir)

-    return_code = uv_install_requirements()
+    airflow_pyproject_toml_file = airflow_sources / "pyproject.toml"
+    return_code = uv_install_requirements(airflow_pyproject_toml_file)

     if return_code != 0:
         print(
PATCH

echo "Patch applied successfully."
