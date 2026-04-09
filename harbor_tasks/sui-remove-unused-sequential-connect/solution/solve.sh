#!/bin/bash
set -e

# Apply the gold patch to remove unused SequentialStore::sequential_connect function
cd /workspace/sui

cat > /tmp/fix.patch << 'PATCH'
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

# Apply the patch
git apply /tmp/fix.patch

# Verify the distinctive line was removed (idempotency check)
if grep -q "Failed to establish sequential connection to store" crates/sui-indexer-alt-framework-store-traits/src/lib.rs; then
    echo "ERROR: Patch not applied correctly - distinctive line still exists"
    exit 1
fi

echo "Patch applied successfully"
