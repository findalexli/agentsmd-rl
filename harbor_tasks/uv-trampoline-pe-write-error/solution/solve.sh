#!/usr/bin/env bash
set -euo pipefail

cd /home/user/uv

# Idempotency: check if the fix is already applied
if grep -q 'WriteResources' crates/uv-trampoline-builder/src/lib.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-trampoline-builder/Cargo.toml b/crates/uv-trampoline-builder/Cargo.toml
index c7601bbba2a91..fb8abb03dcb70 100644
--- a/crates/uv-trampoline-builder/Cargo.toml
+++ b/crates/uv-trampoline-builder/Cargo.toml
@@ -22,7 +22,8 @@ workspace = true

 [dependencies]
 uv-fs = { workspace = true }
-fs-err = {workspace = true }
+
+fs-err = { workspace = true }
 tempfile = { workspace = true }
 thiserror = { workspace = true }
 zip = { workspace = true }
diff --git a/crates/uv-trampoline-builder/src/lib.rs b/crates/uv-trampoline-builder/src/lib.rs
index 489eb2c033f68..6dc67226911d7 100644
--- a/crates/uv-trampoline-builder/src/lib.rs
+++ b/crates/uv-trampoline-builder/src/lib.rs
@@ -5,6 +5,8 @@ use std::str::Utf8Error;
 use fs_err::File;
 use thiserror::Error;

+use uv_fs::Simplified;
+
 #[cfg(all(windows, target_arch = "x86"))]
 const LAUNCHER_I686_GUI: &[u8] = include_bytes!("../trampolines/uv-trampoline-i686-gui.exe");

@@ -230,6 +232,12 @@ pub enum Error {
     UnprocessableMetadata,
     #[error("Resources over 2^32 bytes are not supported")]
     ResourceTooLarge,
+    #[error("Failed to update Windows PE resources: {}", path.user_display())]
+    WriteResources {
+        path: PathBuf,
+        #[source]
+        err: io::Error,
+    },
 }

 #[allow(clippy::unnecessary_wraps, unused_variables)]
@@ -278,13 +286,18 @@ fn write_resources(path: &Path, resources: &[(windows::core::PCWSTR, &[u8])]) ->
             BeginUpdateResourceW, EndUpdateResourceW, UpdateResourceW,
         };

+        let map_err = |err: windows::core::Error| Error::WriteResources {
+            path: path.to_path_buf(),
+            err: io::Error::from_raw_os_error(err.code().0),
+        };
+
         let path_str = path
             .as_os_str()
             .encode_wide()
             .chain(std::iter::once(0))
             .collect::<Vec<_>>();
         let handle = BeginUpdateResourceW(windows::core::PCWSTR(path_str.as_ptr()), false)
-            .map_err(|err| Error::Io(io::Error::from_raw_os_error(err.code().0)))?;
+            .map_err(map_err)?;

         for (name, data) in resources {
             UpdateResourceW(
@@ -295,11 +308,10 @@ fn write_resources(path: &Path, resources: &[(windows::core::PCWSTR, &[u8])]) ->
                 Some(data.as_ptr().cast()),
                 u32::try_from(data.len()).map_err(|_| Error::ResourceTooLarge)?,
             )
-            .map_err(|err| Error::Io(io::Error::from_raw_os_error(err.code().0)))?;
+            .map_err(&map_err)?;
         }

-        EndUpdateResourceW(handle, false)
-            .map_err(|err| Error::Io(io::Error::from_raw_os_error(err.code().0)))?;
+        EndUpdateResourceW(handle, false).map_err(map_err)?;
     }

     Ok(())

PATCH

echo "Patch applied successfully."
