#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if already fixed (curl output saved to file, not piped)
if grep -q 'uv-install\.sh' docker/Dockerfile.rocm 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/docker/Dockerfile.rocm b/docker/Dockerfile.rocm
index fe2b1882da0e..6db6d8b83598 100644
--- a/docker/Dockerfile.rocm
+++ b/docker/Dockerfile.rocm
@@ -29,8 +29,11 @@ RUN if [ "$USE_SCCACHE" != "1" ]; then \
         rm -f "$(which sccache)" || true; \
     fi

-# Install UV
-RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/usr/local/bin" sh
+# Install UV — download first, then run, so a curl failure is not masked by the pipe
+RUN curl -LsSf --retry 3 --retry-delay 5 https://astral.sh/uv/install.sh -o /tmp/uv-install.sh \
+    && env UV_INSTALL_DIR="/usr/local/bin" sh /tmp/uv-install.sh \
+    && rm -f /tmp/uv-install.sh \
+    && uv --version

 # This timeout (in seconds) is necessary when installing some dependencies via uv since it's likely to time out
 # Reference: https://github.com/astral-sh/uv/pull/1694

PATCH

echo "Patch applied successfully."
