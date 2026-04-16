#!/bin/bash
set -e

# Change to the dagster repository
cd /workspace/dagster

# Idempotency check: verify the fix is not already applied
if grep -q "pytest_runtest_setup" python_modules/libraries/dagster-docker/dagster_docker_tests/conftest.py; then
    echo "Fix already applied. Skipping."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | patch -p1
diff --git a/python_modules/libraries/dagster-docker/dagster_docker_tests/conftest.py b/python_modules/libraries/dagster-docker/dagster_docker_tests/conftest.py
index 9c9b60d3d320e..0d980fb46d12c 100644
--- a/python_modules/libraries/dagster-docker/dagster_docker_tests/conftest.py
+++ b/python_modules/libraries/dagster-docker/dagster_docker_tests/conftest.py
@@ -60,3 +60,21 @@ def _instance(overrides=None):
             yield instance

     return _instance
+
+
+def pytest_runtest_setup(item):
+    if "integration" not in item.keywords:
+        return
+
+    if os.getenv("BUILDKITE"):
+        required = [
+            "DAGSTER_DOCKER_REPOSITORY",
+            "DAGSTER_DOCKER_IMAGE_TAG",
+            "AWS_ACCOUNT_ID",
+            "BUILDKITE_SECRETS_BUCKET",
+        ]
+        missing = [var for var in required if not os.getenv(var)]
+        if missing:
+            pytest.skip(
+                "Docker integration tests require Buildkite env vars: " + ", ".join(missing)
+            )
PATCH

echo "Patch applied successfully!"
