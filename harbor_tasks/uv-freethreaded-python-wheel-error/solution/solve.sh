#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if PythonVersion struct already exists in error.rs, patch is applied
if grep -q 'pub struct PythonVersion' crates/uv-distribution/src/error.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/Cargo.lock b/Cargo.lock
index 40d34b2e7d698..ac122a3977dcd 100644
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -6469,6 +6469,7 @@ dependencies = [
  "uv-pep508",
  "uv-platform-tags",
  "uv-pypi-types",
+ "uv-python",
  "uv-redacted",
  "uv-types",
  "uv-warnings",
diff --git a/crates/uv-distribution/Cargo.toml b/crates/uv-distribution/Cargo.toml
index 2bdcccd63eb66..d468858e36037 100644
--- a/crates/uv-distribution/Cargo.toml
+++ b/crates/uv-distribution/Cargo.toml
@@ -34,6 +34,7 @@ uv-pep440 = { workspace = true }
 uv-pep508 = { workspace = true }
 uv-platform-tags = { workspace = true }
 uv-pypi-types = { workspace = true }
+uv-python = { workspace = true }
 uv-redacted = { workspace = true }
 uv-types = { workspace = true }
 uv-warnings = { workspace = true }
diff --git a/crates/uv-distribution/src/distribution_database.rs b/crates/uv-distribution/src/distribution_database.rs
index c3e0f4f32797e..528a2cc78502f 100644
--- a/crates/uv-distribution/src/distribution_database.rs
+++ b/crates/uv-distribution/src/distribution_database.rs
@@ -32,6 +32,9 @@ use uv_types::{BuildContext, BuildStack};
 use uv_warnings::warn_user_once;

 use crate::archive::Archive;
+use uv_python::PythonVariant;
+
+use crate::error::PythonVersion;
 use crate::metadata::{ArchiveMetadata, Metadata};
 use crate::source::SourceDistributionBuilder;
 use crate::{Error, LocalWheel, Reporter, RequiresDist};
@@ -431,13 +434,27 @@ impl<'a, Context: BuildContext> DistributionDatabase<'a, Context> {
                 Err(Error::BuiltWheelIncompatibleTargetPlatform {
                     filename: built_wheel.filename,
                     python_platform: tags.python_platform().clone(),
-                    python_version: tags.python_version(),
+                    python_version: PythonVersion {
+                        version: tags.python_version(),
+                        variant: if tags.is_freethreaded() {
+                            PythonVariant::Freethreaded
+                        } else {
+                            PythonVariant::Default
+                        },
+                    },
                 })
             } else {
                 Err(Error::BuiltWheelIncompatibleHostPlatform {
                     filename: built_wheel.filename,
                     python_platform: tags.python_platform().clone(),
-                    python_version: tags.python_version(),
+                    python_version: PythonVersion {
+                        version: tags.python_version(),
+                        variant: if tags.is_freethreaded() {
+                            PythonVariant::Freethreaded
+                        } else {
+                            PythonVariant::Default
+                        },
+                    },
                 })
             };
         }
diff --git a/crates/uv-distribution/src/error.rs b/crates/uv-distribution/src/error.rs
index cefbd46aae393..b885fc1ef4262 100644
--- a/crates/uv-distribution/src/error.rs
+++ b/crates/uv-distribution/src/error.rs
@@ -1,3 +1,4 @@
+use std::fmt;
 use std::path::PathBuf;

 use owo_colors::OwoColorize;
@@ -15,9 +16,23 @@ use uv_normalize::PackageName;
 use uv_pep440::{Version, VersionSpecifiers};
 use uv_platform_tags::Platform;
 use uv_pypi_types::{HashAlgorithm, HashDigest};
+use uv_python::PythonVariant;
 use uv_redacted::DisplaySafeUrl;
 use uv_types::AnyErrorBuild;

+#[derive(Debug, Clone, Copy)]
+pub struct PythonVersion {
+    pub(crate) version: (u8, u8),
+    pub(crate) variant: PythonVariant,
+}
+
+impl fmt::Display for PythonVersion {
+    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
+        let (major, minor) = self.version;
+        write!(f, "{major}.{minor}{}", self.variant.executable_suffix())
+    }
+}
+
 #[derive(Debug, thiserror::Error)]
 pub enum Error {
     #[error("Building source distributions is disabled")]
@@ -79,30 +94,28 @@ pub enum Error {
     },
     /// This shouldn't happen, it's a bug in the build backend.
     #[error(
-        "The built wheel `{}` is not compatible with the current Python {}.{} on {}",
+        "The built wheel `{}` is not compatible with the current Python {} on {}",
         filename,
-        python_version.0,
-        python_version.1,
+        python_version,
         python_platform.pretty(),
     )]
     BuiltWheelIncompatibleHostPlatform {
         filename: WheelFilename,
         python_platform: Platform,
-        python_version: (u8, u8),
+        python_version: PythonVersion,
     },
     /// This may happen when trying to cross-install native dependencies without their build backend
     /// being aware that the target is a cross-install.
     #[error(
-        "The built wheel `{}` is not compatible with the target Python {}.{} on {}. Consider using `--no-build` to disable building wheels.",
+        "The built wheel `{}` is not compatible with the target Python {} on {}. Consider using `--no-build` to disable building wheels.",
         filename,
-        python_version.0,
-        python_version.1,
+        python_version,
         python_platform.pretty(),
     )]
     BuiltWheelIncompatibleTargetPlatform {
         filename: WheelFilename,
         python_platform: Platform,
-        python_version: (u8, u8),
+        python_version: PythonVersion,
     },
     #[error("Failed to parse metadata from built wheel")]
     Metadata(#[from] uv_pypi_types::MetadataError),
@@ -269,13 +282,14 @@ impl Error {

 #[cfg(test)]
 mod tests {
-    use super::Error;
+    use super::{Error, PythonVersion};
     use std::str::FromStr;
     use uv_distribution_filename::WheelFilename;
     use uv_platform_tags::{Arch, Os, Platform};
+    use uv_python::PythonVariant;

     #[test]
-    fn built_wheel_error_formats_platform() {
+    fn built_wheel_error_formats_freethreaded_python() {
         let err = Error::BuiltWheelIncompatibleHostPlatform {
             filename: WheelFilename::from_str(
                 "cryptography-47.0.0.dev1-cp315-abi3t-macosx_11_0_arm64.whl",
@@ -288,12 +302,15 @@ mod tests {
                 },
                 Arch::Aarch64,
             ),
-            python_version: (3, 15),
+            python_version: PythonVersion {
+                version: (3, 15),
+                variant: PythonVariant::Freethreaded,
+            },
         };

         assert_eq!(
             err.to_string(),
-            "The built wheel `cryptography-47.0.0.dev1-cp315-abi3t-macosx_11_0_arm64.whl` is not compatible with the current Python 3.15 on macOS aarch64"
+            "The built wheel `cryptography-47.0.0.dev1-cp315-abi3t-macosx_11_0_arm64.whl` is not compatible with the current Python 3.15t on macOS aarch64"
         );
     }

@@ -308,7 +325,10 @@ mod tests {
                 },
                 Arch::X86_64,
             ),
-            python_version: (3, 12),
+            python_version: PythonVersion {
+                version: (3, 12),
+                variant: PythonVariant::Default,
+            },
         };

         assert_eq!(
diff --git a/crates/uv-platform-tags/src/tags.rs b/crates/uv-platform-tags/src/tags.rs
index a8f26ddf9ae08..d8d30c05800b4 100644
--- a/crates/uv-platform-tags/src/tags.rs
+++ b/crates/uv-platform-tags/src/tags.rs
@@ -390,6 +390,10 @@ impl Tags {
         self.python_version
     }

+    pub fn is_freethreaded(&self) -> bool {
+        self.is_freethreaded
+    }
+
     pub fn is_cross(&self) -> bool {
         self.is_cross
     }

PATCH

echo "Patch applied successfully."
