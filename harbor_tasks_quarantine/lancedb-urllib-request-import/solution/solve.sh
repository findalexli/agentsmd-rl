#!/bin/bash
set -e

cd /workspace/lancedb

# Apply the fix: add missing urllib.request import
patch -p1 <<'PATCH'
diff --git a/python/python/lancedb/embeddings/utils.py b/python/python/lancedb/embeddings/utils.py
index 1fefc78bfd..189bbe53c7 100644
--- a/python/python/lancedb/embeddings/utils.py
+++ b/python/python/lancedb/embeddings/utils.py
@@ -10,6 +10,7 @@ import threading
 import threading
 import time
 import urllib.error
+import urllib.request
 import weakref
 import logging
 from functools import wraps
PATCH

# Verify the patch was applied
grep -q "import urllib.request" python/python/lancedb/embeddings/utils.py && echo "Fix applied successfully"
