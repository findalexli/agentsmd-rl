#!/usr/bin/env bash
set -euo pipefail

cd /repo

FILE="crates/uv-client/src/registry_client.rs"

# Idempotency check: if the fix is already applied, skip
if grep -q 'type FlatIndexSlot' "$FILE" 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-client/src/registry_client.rs b/crates/uv-client/src/registry_client.rs
index 2c0cc6e2a5870..37278ed538ef2 100644
--- a/crates/uv-client/src/registry_client.rs
+++ b/crates/uv-client/src/registry_client.rs
@@ -250,7 +250,7 @@ pub struct RegistryClient {
     connectivity: Connectivity,
     /// Client HTTP read timeout.
     read_timeout: Duration,
-    /// The flat index entries for each `--find-links`-style index URL.
+    /// The flat index entries for each `--find-links`-style index URL, with one slot per index.
     flat_indexes: Arc<Mutex<FlatIndexCache>>,
     /// The pyx token store to use for persistent credentials.
     // TODO(charlie): The token store is only needed for `is_known_url`; can we avoid storing it here?
@@ -459,11 +459,15 @@ impl RegistryClient {
         package_name: &PackageName,
         index: &IndexUrl,
     ) -> Result<Vec<FlatIndexEntry>, Error> {
-        // Store the flat index entries in a cache, to avoid redundant fetches. A flat index will
-        // typically contain entries for multiple packages; as such, it's more efficient to cache
-        // the entire index rather than re-fetching it for each package.
-        let mut cache = self.flat_indexes.lock().await;
-        if let Some(entries) = cache.get(index) {
+        // Each flat index gets its own slot, so lookups for the same index share a fetch while
+        // unrelated indexes can proceed concurrently.
+        let flat_index_slot = {
+            let mut cache = self.flat_indexes.lock().await;
+            cache.get_or_insert(index)
+        };
+        let mut flat_index = flat_index_slot.lock().await;
+
+        if let Some(entries) = flat_index.as_ref() {
             return Ok(entries.get(package_name).cloned().unwrap_or_default());
         }

@@ -488,7 +492,7 @@ impl RegistryClient {
             .unwrap_or_default();

         // Write to the cache.
-        cache.insert(index.clone(), entries_by_package);
+        *flat_index = Some(entries_by_package);

         Ok(package_entries)
     }
@@ -1274,25 +1278,22 @@ impl From<IndexStatusCodeDecision> for SimpleMetadataSearchOutcome {

 /// A map from [`IndexUrl`] to [`FlatIndexEntry`] entries found at the given URL, indexed by
 /// [`PackageName`].
-#[derive(Default, Debug, Clone)]
-struct FlatIndexCache(FxHashMap<IndexUrl, FxHashMap<PackageName, Vec<FlatIndexEntry>>>);
+#[derive(Default, Debug)]
+struct FlatIndexCache(FxHashMap<IndexUrl, FlatIndexSlot>);

 impl FlatIndexCache {
-    /// Get the entries for a given index URL.
-    fn get(&self, index: &IndexUrl) -> Option<&FxHashMap<PackageName, Vec<FlatIndexEntry>>> {
-        self.0.get(index)
-    }
-
-    /// Insert the entries for a given index URL.
-    fn insert(
-        &mut self,
-        index: IndexUrl,
-        entries: FxHashMap<PackageName, Vec<FlatIndexEntry>>,
-    ) -> Option<FxHashMap<PackageName, Vec<FlatIndexEntry>>> {
-        self.0.insert(index, entries)
+    /// Return the per-index slot for this flat index, creating it on first access.
+    fn get_or_insert(&mut self, index: &IndexUrl) -> FlatIndexSlot {
+        self.0
+            .entry(index.clone())
+            .or_insert_with(|| Arc::new(Mutex::new(None)))
+            .clone()
     }
 }

+type FlatIndexEntriesByPackage = FxHashMap<PackageName, Vec<FlatIndexEntry>>;
+type FlatIndexSlot = Arc<Mutex<Option<FlatIndexEntriesByPackage>>>;
+
 #[derive(Default, Debug, rkyv::Archive, rkyv::Deserialize, rkyv::Serialize)]
 #[rkyv(derive(Debug))]
 pub struct VersionFiles {

PATCH

echo "Patch applied successfully."
