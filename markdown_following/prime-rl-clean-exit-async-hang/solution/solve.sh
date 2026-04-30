#!/usr/bin/env bash
set -euo pipefail

FILE="/workspace/prime-rl/src/prime_rl/utils/utils.py"

# Idempotency: check if already patched
if grep -q 'sys\.exit(1)' "$FILE" 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git -C /workspace/prime-rl apply - <<'PATCH'
diff --git a/src/prime_rl/utils/utils.py b/src/prime_rl/utils/utils.py
index d52a1b1ec7..81a4df7357 100644
--- a/src/prime_rl/utils/utils.py
+++ b/src/prime_rl/utils/utils.py
@@ -3,6 +3,7 @@
 import importlib
 import os
 import subprocess
+import sys
 from collections import defaultdict
 from contextlib import contextmanager
 from pathlib import Path
@@ -129,10 +130,13 @@ async def async_wrapper(*args, **kwargs):
                 ret = await func(*args, **kwargs)
                 wandb.finish()
                 return ret
-            except Exception as e:
+            except Exception:
                 get_logger().opt(exception=True).error(f"Fatal error in {func.__name__}")
                 wandb.finish(exit_code=1)
-                raise e
+                # sys.exit raises SystemExit so the finally block still runs.
+                # raise alone doesn't terminate the process in an async context —
+                # the event loop swallows it and the process hangs indefinitely.
+                sys.exit(1)
             finally:
                 if dist.is_initialized():
                     dist.destroy_process_group()
@@ -146,10 +150,11 @@ def sync_wrapper(*args, **kwargs):
                 ret = func(*args, **kwargs)
                 wandb.finish()
                 return ret
-            except Exception as e:
+            except Exception:
                 get_logger().opt(exception=True).error(f"Fatal error in {func.__name__}")
                 wandb.finish(exit_code=1)
-                raise e
+                # sys.exit raises SystemExit so the finally block still runs.
+                sys.exit(1)
             finally:
                 if dist.is_initialized():
                     dist.destroy_process_group()

PATCH

echo "Patch applied successfully"
