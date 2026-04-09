#!/bin/bash
set -e

cd /workspace/chroma

# Apply the patch to add error logging
cat <<'PATCH' | git apply -
diff --git a/rust/log-service/src/lib.rs b/rust/log-service/src/lib.rs
index b8d331550ac..d1bc267e99c 100644
--- a/rust/log-service/src/lib.rs
+++ b/rust/log-service/src/lib.rs
@@ -2068,15 +2068,17 @@ impl LogServer {
                 )));
             }
             Err(err) => {
+                tracing::error!(err = %err, "get_log_from_handle failure");
                 return Err(Status::unknown(err.to_string()));
             }
         };
         let mut messages = Vec::with_capacity(push_logs.records.len());
         for record in push_logs.records {
             let mut buf = vec![];
-            record
-                .encode(&mut buf)
-                .map_err(|err| Status::unknown(err.to_string()))?;
+            record.encode(&mut buf).map_err(|err| {
+                tracing::error!(err = %err, "proto encode failure");
+                Status::unknown(err.to_string())
+            })?;
             messages.push(buf);
         }
         let record_count = messages.len() as i32;
@@ -2089,7 +2091,10 @@ impl LogServer {
                     "batching",
                 ));
             }
-            Err(err) => return Err(Status::new(err.code().into(), err.to_string())),
+            Err(err) => {
+                tracing::error!(err = %err, "append_many failure");
+                return Err(Status::new(err.code().into(), err.to_string()));
+            }
         };
         if let Some(cache) = self.cache.as_ref() {
             let cache_key = cache_key_for_manifest_and_etag(collection_id);
PATCH

# Verify the distinctive line is now present
grep -q 'tracing::error!(err = %err, "get_log_from_handle failure")' rust/log-service/src/lib.rs \
    && echo "Patch applied successfully" \
    || (echo "Patch failed to apply" && exit 1)
