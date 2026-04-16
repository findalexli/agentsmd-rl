#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch - remove unused SequentialStore::sequential_connect method
cat <<'PATCH' | git apply -
diff --git a/crates/sui-indexer-alt-framework-store-traits/src/lib.rs b/crates/sui-indexer-alt-framework-store-traits/src/lib.rs
index 6918083d78daa..5b02478283d51 100644
--- a/crates/sui-indexer-alt-framework-store-traits/src/lib.rs
+++ b/crates/sui-indexer-alt-framework-store-traits/src/lib.rs
@@ -3,7 +3,6 @@

 use std::time::Duration;

-use anyhow::Context;
 use async_trait::async_trait;
 use chrono::DateTime;
 use chrono::Utc;
@@ -170,13 +169,6 @@ pub trait SequentialStore: for<'c> Store<Connection<'c> = Self::SequentialConnec
     where
         Self: 'c;

-    async fn sequential_connect<'c>(&'c self) -> anyhow::Result<Self::SequentialConnection<'c>> {
-        Ok(self
-            .connect()
-            .await
-            .context("Failed to establish sequential connection to store")?)
-    }
-
     async fn transaction<'a, R, F>(&self, f: F) -> anyhow::Result<R>
     where
         R: Send + 'a,
PATCH

# Idempotency check - verify the distinctive line was removed
if grep -q "sequential_connect" crates/sui-indexer-alt-framework-store-traits/src/lib.rs; then
    echo "ERROR: sequential_connect still exists in the file"
    exit 1
fi

echo "Patch applied successfully - removed unused SequentialStore::sequential_connect method"
