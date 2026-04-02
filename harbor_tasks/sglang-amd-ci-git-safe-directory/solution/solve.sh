#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Check if already applied (look for safe.directory in either file)
if grep -q 'safe\.directory.*sglang-checkout' scripts/ci/amd/amd_ci_start_container.sh 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/scripts/ci/amd/amd_ci_start_container.sh b/scripts/ci/amd/amd_ci_start_container.sh
index 721a3e5dc6ac..327da9348943 100755
--- a/scripts/ci/amd/amd_ci_start_container.sh
+++ b/scripts/ci/amd/amd_ci_start_container.sh
@@ -241,3 +241,8 @@ docker run -dt --user root --device=/dev/kfd ${DEVICE_FLAG} \
   -w /sglang-checkout \
   --name ci_sglang \
   "${IMAGE}"
+
+# The checkout is owned by the runner (non-root) but the container runs as
+# root.  Git >= 2.35.2 rejects cross-user repos; mark the mount as safe so
+# setuptools-scm / vcs_versioning can resolve the package version.
+docker exec ci_sglang git config --global --add safe.directory /sglang-checkout
diff --git a/scripts/ci/amd/amd_ci_start_container_disagg.sh b/scripts/ci/amd/amd_ci_start_container_disagg.sh
index 70de85dff91e..6ae28f82b13c 100755
--- a/scripts/ci/amd/amd_ci_start_container_disagg.sh
+++ b/scripts/ci/amd/amd_ci_start_container_disagg.sh
@@ -263,3 +263,8 @@ docker run -dt --user root \
   -w /sglang-checkout \
   --name ci_sglang \
   "${IMAGE}"
+
+# The checkout is owned by the runner (non-root) but the container runs as
+# root.  Git >= 2.35.2 rejects cross-user repos; mark the mount as safe so
+# setuptools-scm / vcs_versioning can resolve the package version.
+docker exec ci_sglang git config --global --add safe.directory /sglang-checkout

PATCH

echo "Patch applied successfully."
