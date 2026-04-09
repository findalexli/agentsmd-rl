#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

# Idempotent: skip if already applied
if grep -q 'is_stable_abi' crates/uv-platform-tags/src/abi_tag.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-distribution-filename/Cargo.toml b/crates/uv-distribution-filename/Cargo.toml
index 284e18b7776d4..3fafbff8e1632 100644
--- a/crates/uv-distribution-filename/Cargo.toml
+++ b/crates/uv-distribution-filename/Cargo.toml
@@ -12,6 +12,9 @@ license = { workspace = true }
 [lints]
 workspace = true

+[lib]
+doctest = false
+
 [dependencies]
 uv-cache-key = { workspace = true }
 uv-normalize = { workspace = true }
diff --git a/crates/uv-distribution-filename/src/expanded_tags.rs b/crates/uv-distribution-filename/src/expanded_tags.rs
index a18e1fe336f87..2e53f9cf95c47 100644
--- a/crates/uv-distribution-filename/src/expanded_tags.rs
+++ b/crates/uv-distribution-filename/src/expanded_tags.rs
@@ -14,7 +14,7 @@ use crate::wheel_tag::{WheelTag, WheelTagLarge, WheelTagSmall};
 /// The expanded wheel tags as stored in a `WHEEL` file.
 ///
 /// For example, if a wheel filename included `py2.py3-none-any`, the `WHEEL` file would include:
-/// ```
+/// ```text
 /// Tag: py2-none-any
 /// Tag: py3-none-any
 /// ```
diff --git a/crates/uv-distribution-filename/src/wheel.rs b/crates/uv-distribution-filename/src/wheel.rs
index c256931e450eb..f3be4a75370ff 100644
--- a/crates/uv-distribution-filename/src/wheel.rs
+++ b/crates/uv-distribution-filename/src/wheel.rs
@@ -486,4 +486,19 @@ mod tests {
         let parsed = WheelFilename::from_str(filename).unwrap();
         assert_eq!(filename, parsed.to_string());
     }
+
+    #[test]
+    fn abi3t_tags() {
+        let filename =
+            WheelFilename::from_str("foo-1.2.3-cp315-abi3t-manylinux_2_17_x86_64.whl").unwrap();
+        assert_eq!(filename.abi_tags(), &[AbiTag::Abi3T]);
+    }
+
+    #[test]
+    fn compressed_abi3_abi3t_tags() {
+        let filename =
+            WheelFilename::from_str("foo-1.2.3-cp315-abi3.abi3t-manylinux_2_17_x86_64.whl")
+                .unwrap();
+        assert_eq!(filename.abi_tags(), &[AbiTag::Abi3, AbiTag::Abi3T]);
+    }
 }
diff --git a/crates/uv-distribution-types/src/prioritized_distribution.rs b/crates/uv-distribution-types/src/prioritized_distribution.rs
index 230ff3401a4e4..a3b6724eac04e 100644
--- a/crates/uv-distribution-types/src/prioritized_distribution.rs
+++ b/crates/uv-distribution-types/src/prioritized_distribution.rs
@@ -926,9 +926,10 @@ fn implied_python_markers(filename: &WheelFilename) -> MarkerTree {
     let mut marker = MarkerTree::FALSE;

-    // If any ABI tag is `abi3` (the stable ABI), the python tag represents a minimum version
-    // rather than an exact version. For example, `cp39-abi3` means "compatible with CPython 3.9+".
-    let is_abi3 = filename.abi_tags().contains(&AbiTag::Abi3);
+    // If any ABI tag is a stable ABI (`abi3` or `abi3t`), the python tag represents a minimum
+    // version rather than an exact version. For example, `cp39-abi3` means "compatible with
+    // CPython 3.9+".
+    let is_abi3 = filename.abi_tags().iter().any(|tag| tag.is_stable_abi());

     for python_tag in filename.python_tags() {
         // First, construct the version marker based on the tag
@@ -1158,6 +1159,10 @@ mod tests {
             "example-1.0-cp312-abi3-any.whl",
             "python_full_version >= '3.12' and platform_python_implementation == 'CPython'",
         );
+        assert_python_markers(
+            "example-1.0-cp315-abi3t-any.whl",
+            "python_full_version >= '3.15' and platform_python_implementation == 'CPython'",
+        );
         assert_python_markers(
             "example-1.0-cp3-abi3-any.whl",
             "python_full_version >= '3' and platform_python_implementation == 'CPython'",
@@ -1192,5 +1197,9 @@ mod tests {
             "example-1.0-cp39-abi3-manylinux_2_28_x86_64.whl",
             "python_full_version >= '3.9' and platform_python_implementation == 'CPython' and sys_platform == 'linux' and platform_machine == 'x86_64'",
         );
+        assert_implied_markers(
+            "example-1.0-cp315-abi3t-manylinux_2_28_x86_64.whl",
+            "python_full_version >= '3.15' and platform_python_implementation == 'CPython' and sys_platform == 'linux' and platform_machine == 'x86_64'",
+        );
     }
 }
diff --git a/crates/uv-distribution-types/src/requires_python.rs b/crates/uv-distribution-types/src/requires_python.rs
index 80f94b27a39fe..288af4085e935 100644
--- a/crates/uv-distribution-types/src/requires_python.rs
+++ b/crates/uv-distribution-types/src/requires_python.rs
@@ -378,7 +378,7 @@ impl RequiresPython {
     /// sensitivity, we return `true` if the tags are unknown.
     pub fn matches_wheel_tag(&self, wheel: &WheelFilename) -> bool {
         wheel.abi_tags().iter().any(|abi_tag| {
-            if *abi_tag == AbiTag::Abi3 {
+            if abi_tag.is_stable_abi() {
                 // Universal tags are allowed.
                 true
             } else if *abi_tag == AbiTag::None {
diff --git a/crates/uv-platform-tags/src/abi_tag.rs b/crates/uv-platform-tags/src/abi_tag.rs
index d9c7efa31f9a4..c4ac893d215c3 100644
--- a/crates/uv-platform-tags/src/abi_tag.rs
+++ b/crates/uv-platform-tags/src/abi_tag.rs
@@ -108,6 +108,8 @@ pub enum AbiTag {
     None,
     /// Ex) `abi3`
     Abi3,
+    /// Ex) `abi3t`
+    Abi3T,
     /// Ex) `cp39m`, `cp310t`
     CPython {
         python_version: (u8, u8),
@@ -128,11 +130,17 @@ pub enum AbiTag {
 }

 impl AbiTag {
+    /// Return `true` if this is one of the stable ABI tags.
+    pub fn is_stable_abi(self) -> bool {
+        matches!(self, Self::Abi3 | Self::Abi3T)
+    }
+
     /// Return a pretty string representation of the ABI tag.
     pub fn pretty(self) -> Option<String> {
         match self {
             Self::None => None,
             Self::Abi3 => None,
+            Self::Abi3T => Some("stable ABI for free-threaded CPython".to_string()),
             Self::CPython {
                 variant,
                 python_version,
@@ -178,6 +186,7 @@ impl std::fmt::Display for AbiTag {
         match self {
             Self::None => write!(f, "none"),
             Self::Abi3 => write!(f, "abi3"),
+            Self::Abi3T => write!(f, "abi3t"),
             Self::CPython {
                 variant,
                 python_version: (major, minor),
@@ -289,6 +298,8 @@ impl FromStr for AbiTag {
             Ok(Self::None)
         } else if s == "abi3" {
             Ok(Self::Abi3)
+        } else if s == "abi3t" {
+            Ok(Self::Abi3T)
         } else if let Some(cp) = s.strip_prefix("cp") {
             // Ex) `cp39m`, `cp310t`
             let version_end = cp.find(|c: char| !c.is_ascii_digit()).unwrap_or(cp.len());
@@ -463,6 +474,18 @@ mod tests {
     fn abi3() {
         assert_eq!(AbiTag::from_str("abi3"), Ok(AbiTag::Abi3));
         assert_eq!(AbiTag::Abi3.to_string(), "abi3");
+        assert!(AbiTag::Abi3.is_stable_abi());
+    }
+
+    #[test]
+    fn abi3t() {
+        assert_eq!(AbiTag::from_str("abi3t"), Ok(AbiTag::Abi3T));
+        assert_eq!(AbiTag::Abi3T.to_string(), "abi3t");
+        assert!(AbiTag::Abi3T.is_stable_abi());
+        assert_eq!(
+            AbiTag::Abi3T.pretty(),
+            Some("stable ABI for free-threaded CPython".to_string())
+        );
     }

     #[test]
diff --git a/crates/uv-platform-tags/src/tags.rs b/crates/uv-platform-tags/src/tags.rs
index d8d30c05800b4..2f063ecfe0972 100644
--- a/crates/uv-platform-tags/src/tags.rs
+++ b/crates/uv-platform-tags/src/tags.rs
@@ -178,12 +178,24 @@ impl Tags {
                 platform_tag.clone(),
             ));
         }
-        // 2. abi3 and no abi (e.g. executable binary)
+        // 2. abi3/abi3t and no abi (e.g. executable binary)
         if let Implementation::CPython { variant } = implementation {
-            // For some reason 3.2 is the minimum python for the cp abi
-            for minor in (2..=python_version.1).rev() {
-                // No abi3 for free-threading python
-                if !variant.contains(CPythonAbiVariants::Freethreading) {
+            // `abi3` starts at Python 3.2, while `abi3t` starts at Python 3.15.
+            let stable_abi_minor = if variant.contains(CPythonAbiVariants::Freethreading) {
+                15
+            } else {
+                2
+            };
+            for minor in (stable_abi_minor..=python_version.1).rev() {
+                if variant.contains(CPythonAbiVariants::Freethreading) {
+                    for platform_tag in &platform_tags {
+                        tags.push((
+                            implementation.language_tag((python_version.0, minor)),
+                            AbiTag::Abi3T,
+                            platform_tag.clone(),
+                        ));
+                    }
+                } else {
                     for platform_tag in &platform_tags {
                         tags.push((
                             implementation.language_tag((python_version.0, minor)),
@@ -315,10 +327,12 @@ impl Tags {
         wheel_platform_tags: &[PlatformTag],
     ) -> TagCompatibility {
         // On free-threaded Python, check if any wheel ABI tag is compatible.
-        // Only `none` (pure Python) and free-threaded CPython ABIs (e.g., `cp313t`) are compatible.
+        // Only `none` (pure Python), `abi3t`, and free-threaded CPython ABIs
+        // (e.g., `cp313t`) are compatible.
         if self.is_freethreaded {
             let has_compatible_abi = wheel_abi_tags.iter().any(|abi| match abi {
                 AbiTag::None => true,
+                AbiTag::Abi3T => true,
                 AbiTag::CPython { variant, .. } => {
                     variant.contains(CPythonAbiVariants::Freethreading)
                 }
@@ -2690,4 +2704,68 @@ mod tests {
         "
         );
     }
+
+    #[test]
+    fn test_system_tags_freethreaded_include_abi3t() {
+        let tags = Tags::from_env(
+            &Platform::new(
+                Os::Manylinux {
+                    major: 2,
+                    minor: 28,
+                },
+                Arch::X86_64,
+            ),
+            (3, 15),
+            "cpython",
+            (3, 15),
+            false,
+            true,
+            false,
+        )
+        .unwrap();
+
+        assert_snapshot!(
+            tags,
+            @"
+        cp315-cp315t-linux_x86_64
+        cp315-abi3t-linux_x86_64
+        cp315-none-linux_x86_64
+        py315-none-linux_x86_64
+        py3-none-linux_x86_64
+        py314-none-linux_x86_64
+        py313-none-linux_x86_64
+        py312-none-linux_x86_64
+        py311-none-linux_x86_64
+        py310-none-linux_x86_64
+        py39-none-linux_x86_64
+        py38-none-linux_x86_64
+        py37-none-linux_x86_64
+        py36-none-linux_x86_64
+        py35-none-linux_x86_64
+        py34-none-linux_x86_64
+        py33-none-linux_x86_64
+        py32-none-linux_x86_64
+        py31-none-linux_x86_64
+        py30-none-linux_x86_64
+        cp315-none-any
+        py315-none-any
+        py3-none-any
+        py314-none-any
+        py313-none-any
+        py312-none-any
+        py311-none-any
+        py310-none-any
+        py39-none-any
+        py38-none-any
+        py37-none-any
+        py36-none-any
+        py35-none-any
+        py34-none-any
+        py33-none-any
+        py32-none-any
+        py31-none-any
+        py30-none-any
+        "
+        );
+    }
 }

PATCH

echo "Patch applied successfully."
