#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotency: if the patch is already applied, skip.
if grep -q "_retry_urlopen" dev/check_whitespace_only.py; then
    echo "Patch already applied. Skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/dev/check_whitespace_only.py b/dev/check_whitespace_only.py
index 603b3dad3adb7..464c5f5720445 100755
--- a/dev/check_whitespace_only.py
+++ b/dev/check_whitespace_only.py
@@ -8,11 +8,37 @@
 import json
 import os
 import sys
+import time
+import urllib.error
 import urllib.request
 from typing import cast

 BYPASS_LABEL = "allow-whitespace-only"

+_MAX_ATTEMPTS = 3
+
+
+def _is_retryable(exc: Exception) -> bool:
+    match exc:
+        case urllib.error.HTTPError(code=code):
+            return code >= 500
+        case urllib.error.URLError():
+            return True
+        case _:
+            return False
+
+
+def _retry_urlopen(request: urllib.request.Request, timeout: int = 30) -> str:
+    for i in range(_MAX_ATTEMPTS):
+        try:
+            with urllib.request.urlopen(request, timeout=timeout) as response:
+                return cast(str, response.read().decode("utf-8"))
+        except Exception as exc:
+            if not _is_retryable(exc) or i == _MAX_ATTEMPTS - 1:
+                raise
+            time.sleep(2**i)
+    raise RuntimeError("unreachable")
+

 def github_api_request(url: str, accept: str) -> str:
     headers = {
@@ -24,15 +50,13 @@ def github_api_request(url: str, accept: str) -> str:
         headers["Authorization"] = f"Bearer {github_token}"

     request = urllib.request.Request(url, headers=headers)
-    with urllib.request.urlopen(request, timeout=30) as response:
-        return cast(str, response.read().decode("utf-8"))
+    return _retry_urlopen(request)


 def get_pr_diff(owner: str, repo: str, pull_number: int) -> str:
     url = f"https://github.com/{owner}/{repo}/pull/{pull_number}.diff"
     request = urllib.request.Request(url)
-    with urllib.request.urlopen(request, timeout=30) as response:
-        return cast(str, response.read().decode("utf-8"))
+    return _retry_urlopen(request)


 def get_pr_labels(owner: str, repo: str, pull_number: int) -> list[str]:
PATCH

echo "Gold patch applied."
