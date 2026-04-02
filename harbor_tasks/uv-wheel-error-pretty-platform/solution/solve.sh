#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if pretty() method already exists, patch is applied
if grep -q 'fn pretty' crates/uv-platform-tags/src/platform.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-distribution/src/error.rs b/crates/uv-distribution/src/error.rs
index e986803115693..cefbd46aae393 100644
--- a/crates/uv-distribution/src/error.rs
+++ b/crates/uv-distribution/src/error.rs
@@ -79,12 +79,11 @@ pub enum Error {
     },
     /// This shouldn't happen, it's a bug in the build backend.
     #[error(
-        "The built wheel `{}` is not compatible with the current Python {}.{} on {} {}",
+        "The built wheel `{}` is not compatible with the current Python {}.{} on {}",
         filename,
         python_version.0,
         python_version.1,
-        python_platform.os(),
-        python_platform.arch(),
+        python_platform.pretty(),
     )]
     BuiltWheelIncompatibleHostPlatform {
         filename: WheelFilename,
@@ -94,12 +93,11 @@ pub enum Error {
     /// This may happen when trying to cross-install native dependencies without their build backend
     /// being aware that the target is a cross-install.
     #[error(
-        "The built wheel `{}` is not compatible with the target Python {}.{} on {} {}. Consider using `--no-build` to disable building wheels.",
+        "The built wheel `{}` is not compatible with the target Python {}.{} on {}. Consider using `--no-build` to disable building wheels.",
         filename,
         python_version.0,
         python_version.1,
-        python_platform.os(),
-        python_platform.arch(),
+        python_platform.pretty(),
     )]
     BuiltWheelIncompatibleTargetPlatform {
         filename: WheelFilename,
@@ -268,3 +266,54 @@ impl Error {
         }
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::Error;
+    use std::str::FromStr;
+    use uv_distribution_filename::WheelFilename;
+    use uv_platform_tags::{Arch, Os, Platform};
+
+    #[test]
+    fn built_wheel_error_formats_platform() {
+        let err = Error::BuiltWheelIncompatibleHostPlatform {
+            filename: WheelFilename::from_str(
+                "cryptography-47.0.0.dev1-cp315-abi3t-macosx_11_0_arm64.whl",
+            )
+            .unwrap(),
+            python_platform: Platform::new(
+                Os::Macos {
+                    major: 11,
+                    minor: 0,
+                },
+                Arch::Aarch64,
+            ),
+            python_version: (3, 15),
+        };
+
+        assert_eq!(
+            err.to_string(),
+            "The built wheel `cryptography-47.0.0.dev1-cp315-abi3t-macosx_11_0_arm64.whl` is not compatible with the current Python 3.15 on macOS aarch64"
+        );
+    }
+
+    #[test]
+    fn built_wheel_error_formats_target_python() {
+        let err = Error::BuiltWheelIncompatibleTargetPlatform {
+            filename: WheelFilename::from_str("py313-0.1.0-py313-none-any.whl").unwrap(),
+            python_platform: Platform::new(
+                Os::Manylinux {
+                    major: 2,
+                    minor: 28,
+                },
+                Arch::X86_64,
+            ),
+            python_version: (3, 12),
+        };
+
+        assert_eq!(
+            err.to_string(),
+            "The built wheel `py313-0.1.0-py313-none-any.whl` is not compatible with the target Python 3.12 on Linux x86_64. Consider using `--no-build` to disable building wheels."
+        );
+    }
+}
diff --git a/crates/uv-platform-tags/src/platform.rs b/crates/uv-platform-tags/src/platform.rs
index c1d02c91580e1..d6eeb4c796ad2 100644
--- a/crates/uv-platform-tags/src/platform.rs
+++ b/crates/uv-platform-tags/src/platform.rs
@@ -40,6 +40,25 @@ impl Platform {
     pub fn arch(&self) -> Arch {
         self.arch
     }
+
+    /// Return a human-readable representation of the platform.
+    pub fn pretty(&self) -> String {
+        let os = match self.os() {
+            Os::Manylinux { .. } | Os::Musllinux { .. } => "Linux",
+            Os::Windows => "Windows",
+            Os::Pyodide { .. } => "Pyodide",
+            Os::Macos { .. } => "macOS",
+            Os::FreeBsd { .. } => "FreeBSD",
+            Os::NetBsd { .. } => "NetBSD",
+            Os::OpenBsd { .. } => "OpenBSD",
+            Os::Dragonfly { .. } => "DragonFly",
+            Os::Illumos { .. } => "Illumos",
+            Os::Haiku { .. } => "Haiku",
+            Os::Android { .. } => "Android",
+            Os::Ios { .. } => "iOS",
+        };
+        format!("{os} {}", self.arch())
+    }
 }

 /// All supported operating systems.
@@ -240,3 +259,34 @@ impl Arch {
         }
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::{Arch, Os, Platform};
+
+    #[test]
+    fn platform_pretty_macos() {
+        let platform = Platform::new(
+            Os::Macos {
+                major: 11,
+                minor: 0,
+            },
+            Arch::Aarch64,
+        );
+
+        assert_eq!(platform.pretty(), "macOS aarch64");
+    }
+
+    #[test]
+    fn platform_pretty_manylinux() {
+        let platform = Platform::new(
+            Os::Manylinux {
+                major: 2,
+                minor: 28,
+            },
+            Arch::X86_64,
+        );
+
+        assert_eq!(platform.pretty(), "Linux x86_64");
+    }
+}

PATCH

echo "Patch applied successfully."
