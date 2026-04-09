#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied (check for the new monorepo regex)
if grep -q 'MONOREPO_PACKAGE_REGEX' turbopack/crates/turbopack-core/src/chunk/chunking/dev.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/turbopack/crates/turbopack-core/src/chunk/chunking/dev.rs b/turbopack/crates/turbopack-core/src/chunk/chunking/dev.rs
index 4f31587898a2b..37584a68691c3 100644
--- a/turbopack/crates/turbopack-core/src/chunk/chunking/dev.rs
+++ b/turbopack/crates/turbopack-core/src/chunk/chunking/dev.rs
@@ -125,8 +125,9 @@ pub async fn app_vendors_split<'l>(
     )
     .await?
     {
-        folder_split(app_chunk_items, 0, key.into(), split_context).await?;
+        package_name_split(app_chunk_items, key, split_context).await?;
     }
+
     let mut key = format!("{}-vendors", name);
     if !handle_split_group(
         &mut vendors_chunk_items,
@@ -146,8 +147,8 @@ pub async fn app_vendors_split<'l>(
     Ok(())
 }

-/// Split chunk items by node_modules package name. Continues splitting with
-/// [folder_split] if necessary.
+/// Split chunk items by package name (either by node_modules or monorepo package). Continues
+/// splitting with [folder_split] if necessary.
 #[tracing::instrument(level = Level::TRACE, skip_all, fields(name = display(&name)))]
 async fn package_name_split<'l>(
     chunk_items: Vec<&'l ChunkItemOrBatchWithInfo>,
@@ -260,10 +261,17 @@ fn is_app_code(ident: &str) -> bool {

 /// Returns the package name of the given `ident`.
 fn package_name(ident: &str) -> &str {
-    static PACKAGE_NAME_REGEX: Lazy<Regex> =
+    static NODE_MODULES_PACKAGE_REGEX: Lazy<Regex> =
         Lazy::new(|| Regex::new(r"/node_modules/((?:@[^/]+/)?[^/]+)").unwrap());
-    if let Some(result) = PACKAGE_NAME_REGEX.find_iter(ident).last() {
+
+    static MONOREPO_PACKAGE_REGEX: Lazy<Regex> =
+        // Use `packages` as it's commonly used in monorepos.
+        Lazy::new(|| Regex::new(r"/packages/((?:@[^/]+/)?[^/]+)").unwrap());
+
+    if let Some(result) = NODE_MODULES_PACKAGE_REGEX.find_iter(ident).last() {
         &result.as_str()["/node_modules/".len()..]
+    } else if let Some(result) = MONOREPO_PACKAGE_REGEX.find_iter(ident).last() {
+        &result.as_str()["/packages/".len()..]
     } else {
         ""
     }
PATCH

echo "Patch applied successfully."
