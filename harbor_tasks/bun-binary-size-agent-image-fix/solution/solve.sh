#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'buildPlatforms.find' .buildkite/ci.mjs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/.buildkite/ci.mjs b/.buildkite/ci.mjs
index 7f7ff102739..362cef0b315 100755
--- a/.buildkite/ci.mjs
+++ b/.buildkite/ci.mjs
@@ -831,9 +831,11 @@ function getBinarySizeStep(releasePlatforms, options, { recordOnly = false } = {
   return {
     key: "binary-size",
     label: `${getBuildkiteEmoji("package")} binary-size`,
-    agents: getEc2Agent({ os: "linux", arch: "aarch64", distro: "amazonlinux", release: "2023" }, options, {
-      instanceType: "c8g.large",
-    }),
+    agents: getEc2Agent(
+      buildPlatforms.find(p => p.os === "linux" && p.arch === "aarch64" && p.distro === "amazonlinux"),
+      options,
+      { instanceType: "c8g.large" },
+    ),
     depends_on: releasePlatforms.map(p => `${getTargetKey(p)}-build-bun`),
     allow_dependency_failure: true,
     soft_fail: !!options.skipSizeCheck,

PATCH

echo "Patch applied successfully."
