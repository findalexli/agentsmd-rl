#!/usr/bin/env bash
set -euo pipefail

cd /workspace/deno

# Idempotent: skip if already applied
if grep -q 'link_package_nvs' libs/npm/resolution/snapshot.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/libs/npm/resolution/snapshot.rs b/libs/npm/resolution/snapshot.rs
index 97150fdea41816..5184b0172e6bf6 100644
--- a/libs/npm/resolution/snapshot.rs
+++ b/libs/npm/resolution/snapshot.rs
@@ -965,12 +965,13 @@ pub fn snapshot_from_lockfile(
   let mut root_packages = HashMap::<PackageReq, NpmPackageId>::with_capacity(
     lockfile.content.packages.specifiers.len(),
   );
-  let link_package_ids = params
+  let link_package_nvs = params
     .link_packages
     .iter()
     .flat_map(|(name, info_vec)| {
-      info_vec.iter().map(move |info| {
-        StackString::from_string(format!("{}@{}", name, info.version))
+      info_vec.iter().map(move |info| PackageNv {
+        name: name.clone(),
+        version: info.version.clone(),
       })
     })
     .collect::<HashSet<_>>();
@@ -1008,7 +1009,7 @@ pub fn snapshot_from_lockfile(
     }

     packages.push(SerializedNpmResolutionSnapshotPackage {
-      dist: if !link_package_ids.contains(key) {
+      dist: if !link_package_nvs.contains(&id.nv) {
         Some(dist_from_incomplete_package_info(
           &id.nv,
           package.integrity.as_deref(),
@@ -1617,4 +1618,68 @@ mod tests {
       }]
     );
   }
+
+  #[tokio::test]
+  async fn test_snapshot_from_lockfile_v5_with_linked_package_with_peer_deps() {
+    let api = TestNpmRegistryApi::default();
+    let lockfile = Lockfile::new(
+      NewLockfileOptions {
+        file_path: PathBuf::from("/deno.lock"),
+        content: r#"{
+          "version": "5",
+          "specifiers": {
+            "npm:@myorg/shared@*": "1.0.0_zod@4.3.6"
+          },
+          "npm": {
+            "@myorg/shared@1.0.0_zod@4.3.6": {
+              "dependencies": ["zod@4.3.6"]
+            },
+            "zod@4.3.6": {}
+          },
+          "workspace": {
+            "packageJson": {
+              "dependencies": [
+                "npm:@myorg/shared@*"
+              ]
+            },
+            "links": {
+              "npm:@myorg/shared@1.0.0": {}
+            }
+          }
+        }"#,
+        overwrite: false,
+      },
+      &api,
+    )
+    .await
+    .unwrap();
+    let link_packages = &HashMap::from([(
+      PackageName::from_str("@myorg/shared"),
+      vec![NpmPackageVersionInfo {
+        version: Version::parse_standard("1.0.0").unwrap(),
+        ..Default::default()
+      }],
+    )]);
+    let snapshot = snapshot_from_lockfile(SnapshotFromLockfileParams {
+      lockfile: &lockfile,
+      link_packages,
+      default_tarball_url: &TestDefaultTarballUrlProvider,
+    })
+    .unwrap();
+
+    let packages = &snapshot.as_serialized().packages;
+    // The linked package (even with peer dep suffix) should have dist: None
+    let shared_pkg = packages
+      .iter()
+      .find(|p| p.id.nv.name.as_str() == "@myorg/shared")
+      .expect("should find @myorg/shared package");
+    assert_eq!(shared_pkg.dist, None);
+
+    // The non-linked peer dep should have dist info
+    let zod_pkg = packages
+      .iter()
+      .find(|p| p.id.nv.name.as_str() == "zod")
+      .expect("should find zod package");
+    assert!(zod_pkg.dist.is_some());
+  }
 }

PATCH

echo "Patch applied successfully."
