#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q '\^\[A-Za-z\]:\[/\\\\\]' turbopack/crates/turbopack-core/src/resolve/parse.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/turbopack/crates/turbopack-core/src/resolve/parse.rs b/turbopack/crates/turbopack-core/src/resolve/parse.rs
index e8af9e865d0c5..6807001d0035b 100644
--- a/turbopack/crates/turbopack-core/src/resolve/parse.rs
+++ b/turbopack/crates/turbopack-core/src/resolve/parse.rs
@@ -90,7 +90,8 @@ fn split_off_query_fragment(mut raw: &str) -> (Pattern, RcStr, RcStr) {
     (Pattern::Constant(RcStr::from(raw)), query, hash)
 }

-static WINDOWS_PATH: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^[A-Za-z]:\\|\\\\").unwrap());
+static WINDOWS_PATH: LazyLock<Regex> =
+    LazyLock::new(|| Regex::new(r"^[A-Za-z]:[/\\]|^\\\\").unwrap());
 static URI_PATH: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^([^/\\:]+:)(.+)$").unwrap());
 static DATA_URI_REMAINDER: LazyLock<Regex> =
     LazyLock::new(|| Regex::new(r"^([^;,]*)(?:;([^,]+))?,(.*)$").unwrap());

PATCH

echo "Patch applied successfully."
