#!/usr/bin/env bash
set -euo pipefail
cd /workspace/slime

# Idempotent: skip if already applied
if grep -q 'trust_env=False' slime/utils/http_utils.py; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/utils/http_utils.py b/slime/utils/http_utils.py
index d7807f3b7a..ede851f6b0 100644
--- a/slime/utils/http_utils.py
+++ b/slime/utils/http_utils.py
@@ -209,6 +209,7 @@ def init_http_client(args):
         _http_client = httpx.AsyncClient(
             limits=httpx.Limits(max_connections=_client_concurrency),
             timeout=httpx.Timeout(None),
+            trust_env=False,  # internal SGLang comm only -- never route through system proxy
         )

     # Optionally initialize distributed POST via Ray without changing interfaces
@@ -243,6 +244,7 @@ def __init__(self, concurrency: int):
             self._client = httpx.AsyncClient(
                 limits=httpx.Limits(max_connections=max(1, concurrency)),
                 timeout=httpx.Timeout(None),
+                trust_env=False,  # internal SGLang comm only -- never route through system proxy
             )

         async def do_post(self, url, payload, max_retries=60, headers=None):

PATCH
