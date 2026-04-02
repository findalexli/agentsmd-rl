#!/usr/bin/env bash
set -euo pipefail

cd /repos/uv

TARGET="scripts/check_system_python.py"

# Idempotency: check if already patched
if grep -q 'shutil.which("pylint")' "$TARGET" && ! grep -q 'os.name != "nt"' "$TARGET"; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/scripts/check_system_python.py b/scripts/check_system_python.py
index 3518d1578db88..5fe740f21eed2 100755
--- a/scripts/check_system_python.py
+++ b/scripts/check_system_python.py
@@ -152,13 +152,9 @@ def install_package(*, uv: str, package: str, version: str = None):
         if code.returncode != 0:
             raise Exception("The package `pylint` isn't installed (but should be).")

-        # TODO(charlie): Windows is failing to find the `pylint` binary, despite
-        # confirmation that it's being written to the intended location.
-        if os.name != "nt":
-            logging.info("Checking that `pylint` is in the path.")
-            code = subprocess.run(["which", "pylint"], cwd=temp_dir)
-            if code.returncode != 0:
-                raise Exception("The package `pylint` isn't in the path.")
+        logging.info("Checking that `pylint` is in the path.")
+        if shutil.which("pylint") is None:
+            raise Exception("The package `pylint` isn't in the path.")

         # Uninstall the package (`pylint`).
         logging.info("Uninstalling the package `pylint`.")

PATCH

echo "Patch applied successfully."
