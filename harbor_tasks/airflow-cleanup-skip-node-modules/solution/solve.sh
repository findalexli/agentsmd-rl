#!/bin/bash
set -e

cd /workspace/airflow

# Apply the fix: Speed up cleanup_python_generated_files by skipping node_modules and hidden dirs
patch -p1 << 'PATCH'
diff --git a/dev/breeze/src/airflow_breeze/utils/path_utils.py b/dev/breeze/src/airflow_breeze/utils/path_utils.py
index 03877d6476163..7f2625a0bcca9 100644
--- a/dev/breeze/src/airflow_breeze/utils/path_utils.py
+++ b/dev/breeze/src/airflow_breeze/utils/path_utils.py
@@ -418,22 +418,26 @@ def cleanup_python_generated_files():
     if get_verbose():
         console_print("[info]Cleaning .pyc and __pycache__")
     permission_errors = []
-    for path in AIRFLOW_ROOT_PATH.rglob("*.pyc"):
-        try:
-            path.unlink()
-        except FileNotFoundError:
-            # File has been removed in the meantime.
-            pass
-        except PermissionError:
-            permission_errors.append(path)
-    for path in AIRFLOW_ROOT_PATH.rglob("__pycache__"):
-        try:
-            shutil.rmtree(path)
-        except FileNotFoundError:
-            # File has been removed in the meantime.
-            pass
-        except PermissionError:
-            permission_errors.append(path)
+    for dirpath, dirnames, filenames in os.walk(AIRFLOW_ROOT_PATH):
+        # Skip node_modules and hidden directories (.*) — modify in place to prune os.walk
+        dirnames[:] = [d for d in dirnames if d != "node_modules" and not d.startswith(".")]
+        for filename in filenames:
+            if filename.endswith(".pyc"):
+                path = Path(dirpath) / filename
+                try:
+                    path.unlink()
+                except FileNotFoundError:
+                    pass
+                except PermissionError:
+                    permission_errors.append(path)
+        if Path(dirpath).name == "__pycache__":
+            try:
+                shutil.rmtree(dirpath)
+            except FileNotFoundError:
+                pass
+            except PermissionError:
+                permission_errors.append(Path(dirpath))
+            dirnames.clear()
     if permission_errors:
         if platform.uname().system.lower() == "linux":
             console_print("[warning]There were files that you could not clean-up:\n")
PATCH

echo "Fix applied successfully"
