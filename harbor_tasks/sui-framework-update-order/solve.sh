#!/bin/bash
set -e

cd /workspace/sui

# Check if already applied
if grep -q "fs_extra::dir::copy(out_dir.join(COMPILED_PACKAGES_DIR)" crates/sui-framework/tests/build-system-packages.rs; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/crates/sui-framework/tests/build-system-packages.rs b/crates/sui-framework/tests/build-system-packages.rs
index 0736efc025058..5847490036ee1 100644
--- a/crates/sui-framework/tests/build-system-packages.rs
+++ b/crates/sui-framework/tests/build-system-packages.rs
@@ -24,15 +24,7 @@ const PUBLISHED_API_FILE: &str = "published_api.txt";
 #[tokio::test]
 async fn build_system_packages() {
     let tempdir = tempfile::tempdir().unwrap();
-    let out_dir = if std::env::var_os("UPDATE").is_some() {
-        let crate_root = Path::new(CRATE_ROOT);
-        let _ = std::fs::remove_dir_all(crate_root.join(COMPILED_PACKAGES_DIR));
-        let _ = std::fs::remove_dir_all(crate_root.join(DOCS_DIR));
-        let _ = std::fs::remove_file(crate_root.join(PUBLISHED_API_FILE));
-        crate_root
-    } else {
-        tempdir.path()
-    };
+    let out_dir = tempdir.path();

     std::fs::create_dir_all(out_dir.join(COMPILED_PACKAGES_DIR)).unwrap();
     std::fs::create_dir_all(out_dir.join(DOCS_DIR)).unwrap();
@@ -62,7 +54,29 @@ async fn build_system_packages() {
         out_dir,
     )
     .await;
-    check_diff(Path::new(CRATE_ROOT), out_dir)
+
+    let crate_root = Path::new(CRATE_ROOT);
+    if std::env::var_os("UPDATE").is_some() {
+        for dir in [COMPILED_PACKAGES_DIR, DOCS_DIR] {
+            let p = crate_root.join(dir);
+            if p.exists() {
+                std::fs::remove_dir_all(&p).unwrap();
+            }
+        }
+        let api_file = crate_root.join(PUBLISHED_API_FILE);
+        if api_file.exists() {
+            std::fs::remove_file(&api_file).unwrap();
+        }
+        let copy_opts = CopyOptions::new().overwrite(true);
+        fs_extra::dir::copy(out_dir.join(COMPILED_PACKAGES_DIR), crate_root, &copy_opts).unwrap();
+        fs_extra::dir::copy(out_dir.join(DOCS_DIR), crate_root, &copy_opts).unwrap();
+        std::fs::copy(
+            out_dir.join(PUBLISHED_API_FILE),
+            crate_root.join(PUBLISHED_API_FILE),
+        )
+        .unwrap();
+    }
+    check_diff(crate_root, out_dir)
 }

 // Verify that checked-in values are the same as the generated ones
PATCH

echo "Patch applied successfully"
