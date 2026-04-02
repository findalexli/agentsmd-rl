#!/usr/bin/env bash
set -euo pipefail

cd /repo

FILE="crates/uv-distribution/src/distribution_database.rs"

# Idempotency check: if the fix is already applied, skip
if grep -q 'is_http_streaming_failed' "$FILE" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-distribution/src/distribution_database.rs b/crates/uv-distribution/src/distribution_database.rs
index 2267408972df0..c3e0f4f32797e 100644
--- a/crates/uv-distribution/src/distribution_database.rs
+++ b/crates/uv-distribution/src/distribution_database.rs
@@ -248,8 +248,8 @@ impl<'a, Context: BuildContext> DistributionDatabase<'a, Context> {
                             return Err(Error::Extract(name, err));
                         }

-                        // If the request failed because streaming is unsupported, download the
-                        // wheel directly.
+                        // If the request failed because streaming was unsupported or failed,
+                        // download the wheel directly.
                         let archive = self
                             .download_wheel(
                                 url,
@@ -314,13 +314,19 @@ impl<'a, Context: BuildContext> DistributionDatabase<'a, Context> {
                         cache: CacheInfo::default(),
                         build: None,
                     }),
-                    Err(Error::Client(err)) if err.is_http_streaming_unsupported() => {
-                        warn!(
-                            "Streaming unsupported for {dist}; downloading wheel to disk ({err})"
-                        );
+                    Err(Error::Extract(name, err)) => {
+                        if err.is_http_streaming_unsupported() {
+                            warn!(
+                                "Streaming unsupported for {dist}; downloading wheel to disk ({err})"
+                            );
+                        } else if err.is_http_streaming_failed() {
+                            warn!("Streaming failed for {dist}; downloading wheel to disk ({err})");
+                        } else {
+                            return Err(Error::Extract(name, err));
+                        }

-                        // If the request failed because streaming is unsupported, download the
-                        // wheel directly.
+                        // If the request failed because streaming was unsupported or failed,
+                        // download the wheel directly.
                         let archive = self
                             .download_wheel(
                                 wheel.url.raw().clone(),

PATCH

echo "Patch applied successfully."
