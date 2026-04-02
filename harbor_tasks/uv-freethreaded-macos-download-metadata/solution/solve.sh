#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if the fix is already applied, exit
if grep -q 'for suffix in ("-debug", "-freethreaded")' crates/uv-python/fetch-download-metadata.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-python/fetch-download-metadata.py b/crates/uv-python/fetch-download-metadata.py
index 13ddfb91bc959..f54acf9c29b33 100755
--- a/crates/uv-python/fetch-download-metadata.py
+++ b/crates/uv-python/fetch-download-metadata.py
@@ -290,14 +290,15 @@ def _parse_ndjson_artifact(
         platform_str = artifact["platform"]
         variant_str = artifact["variant"]

-        # On macOS, debug builds encode "-debug" as a platform suffix rather
-        # than a variant component (e.g. "aarch64-apple-darwin-debug"). Strip
-        # it and promote it to a build option to match the treatment applied
-        # when parsing filenames via the old filename regex.
+        # On macOS, some builds encode build options as platform suffixes
+        # rather than variant components (e.g. "aarch64-apple-darwin-debug",
+        # "aarch64-apple-darwin-freethreaded"). Strip them and promote to
+        # build options.
         platform_build_options: list[str] = []
-        if platform_str.endswith("-debug"):
-            platform_str = platform_str[: -len("-debug")]
-            platform_build_options.append("debug")
+        for suffix in ("-debug", "-freethreaded"):
+            if platform_str.endswith(suffix):
+                platform_str = platform_str[: -len(suffix)]
+                platform_build_options.append(suffix.lstrip("-"))

         flavor, variant_build_options = self._parse_variant(variant_str)
         build_options = platform_build_options + variant_build_options

PATCH

echo "Patch applied successfully."
