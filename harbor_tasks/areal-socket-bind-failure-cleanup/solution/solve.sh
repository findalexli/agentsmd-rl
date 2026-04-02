#!/usr/bin/env bash
set -euo pipefail
cd /workspace/AReaL

# Idempotent: skip if already applied
grep -q 'finally:' areal/utils/network.py && \
  ! grep -q 'raise exc_value' areal/trainer/rl_trainer.py && exit 0

git apply - <<'PATCH'
diff --git a/areal/trainer/rl_trainer.py b/areal/trainer/rl_trainer.py
index 5ec0d2cbe..5c48649f0 100644
--- a/areal/trainer/rl_trainer.py
+++ b/areal/trainer/rl_trainer.py
@@ -1018,5 +1018,4 @@ def __exit__(self, exc_type, exc_value, traceback):
         if exc_type is not None:
             logger.error(f"Training failed with exception: {exc_value}", exc_info=True)
         self.close()
-        if exc_type is not None:
-            raise exc_value
+        return False
diff --git a/areal/trainer/sft_trainer.py b/areal/trainer/sft_trainer.py
index dd66e9482..6f53f4483 100644
--- a/areal/trainer/sft_trainer.py
+++ b/areal/trainer/sft_trainer.py
@@ -403,5 +403,4 @@ def __exit__(self, exc_type, exc_value, traceback):
         if exc_type is not None:
             logger.error(f"Training failed with exception: {exc_value}", exc_info=True)
         self.close()
-        if exc_type is not None:
-            raise exc_value
+        return False
diff --git a/areal/utils/network.py b/areal/utils/network.py
index 199998a7a..7f1effd7c 100644
--- a/areal/utils/network.py
+++ b/areal/utils/network.py
@@ -113,15 +113,17 @@ def is_port_free(port: int) -> bool:
     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     try:
         sock.bind(("", port))
-        sock.close()
     except OSError:
         return False
+    finally:
+        sock.close()

     # Check UDP
     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     try:
         sock.bind(("", port))
-        sock.close()
         return True
     except OSError:
         return False
+    finally:
+        sock.close()

PATCH
