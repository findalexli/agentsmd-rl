#!/bin/bash
set -e

cd /workspace/selenium

# Idempotency check - skip if patch already applied
if grep -q "_owns_log_output" py/selenium/webdriver/common/service.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/py/selenium/webdriver/common/service.py b/py/selenium/webdriver/common/service.py
index 1234567..abcdefg 100644
--- a/py/selenium/webdriver/common/service.py
+++ b/py/selenium/webdriver/common/service.py
@@ -58,9 +58,11 @@ class Service(ABC):
         driver_path_env_key: str | None = None,
         **kwargs,
     ) -> None:
+        self._owns_log_output = False
         self.log_output: int | IO[Any] | None
         if isinstance(log_output, str):
             self.log_output = open(log_output, "a+", encoding="utf-8")
+            self._owns_log_output = True
         elif log_output == subprocess.STDOUT:
             self.log_output = None
         elif log_output is None or log_output == subprocess.DEVNULL:
@@ -147,7 +149,7 @@ class Service(ABC):
     def stop(self) -> None:
         """Stops the service."""
         if self.log_output not in {PIPE, subprocess.DEVNULL}:
-            if isinstance(self.log_output, IOBase):
+            if isinstance(self.log_output, IOBase) and self._owns_log_output:
                 self.log_output.close()
             elif isinstance(self.log_output, int):
                 os.close(self.log_output)
PATCH

echo "Patch applied successfully."
