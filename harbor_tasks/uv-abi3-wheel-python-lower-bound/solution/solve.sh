#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

# Idempotency guard: the gold patch introduces this distinctive comment.
if grep -q "If any ABI tag is .abi3. (the stable ABI), the python tag represents a minimum version" \
    crates/uv-distribution-types/src/prioritized_distribution.rs 2>/dev/null; then
    echo "Patch already applied; skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/uv-distribution-types/src/prioritized_distribution.rs b/crates/uv-distribution-types/src/prioritized_distribution.rs
index 7abd7b9d15d61..230ff3401a4e4 100644
--- a/crates/uv-distribution-types/src/prioritized_distribution.rs
+++ b/crates/uv-distribution-types/src/prioritized_distribution.rs
@@ -926,6 +926,10 @@ fn implied_platform_markers(filename: &WheelFilename) -> MarkerTree {
 fn implied_python_markers(filename: &WheelFilename) -> MarkerTree {
     let mut marker = MarkerTree::FALSE;

+    // If any ABI tag is `abi3` (the stable ABI), the python tag represents a minimum version
+    // rather than an exact version. For example, `cp39-abi3` means "compatible with CPython 3.9+".
+    let is_abi3 = filename.abi_tags().contains(&AbiTag::Abi3);
+
     for python_tag in filename.python_tags() {
         // First, construct the version marker based on the tag
         let mut tree = match python_tag {
@@ -934,12 +938,21 @@ fn implied_python_markers(filename: &WheelFilename) -> MarkerTree {
                 return MarkerTree::TRUE;
             }
             LanguageTag::Python { major, minor: None } | LanguageTag::CPythonMajor { major } => {
-                MarkerTree::expression(MarkerExpression::Version {
-                    key: uv_pep508::MarkerValueVersion::PythonVersion,
-                    specifier: VersionSpecifier::equals_star_version(Version::new([u64::from(
-                        *major,
-                    )])),
-                })
+                if is_abi3 {
+                    MarkerTree::expression(MarkerExpression::Version {
+                        key: uv_pep508::MarkerValueVersion::PythonVersion,
+                        specifier: VersionSpecifier::greater_than_equal_version(Version::new([
+                            u64::from(*major),
+                        ])),
+                    })
+                } else {
+                    MarkerTree::expression(MarkerExpression::Version {
+                        key: uv_pep508::MarkerValueVersion::PythonVersion,
+                        specifier: VersionSpecifier::equals_star_version(Version::new([
+                            u64::from(*major),
+                        ])),
+                    })
+                }
             }
             LanguageTag::Python {
                 major,
@@ -956,13 +969,25 @@ fn implied_python_markers(filename: &WheelFilename) -> MarkerTree {
             }
             | LanguageTag::Pyston {
                 python_version: (major, minor),
-            } => MarkerTree::expression(MarkerExpression::Version {
-                key: uv_pep508::MarkerValueVersion::PythonVersion,
-                specifier: VersionSpecifier::equals_star_version(Version::new([
-                    u64::from(*major),
-                    u64::from(*minor),
-                ])),
-            }),
+            } => {
+                if is_abi3 {
+                    MarkerTree::expression(MarkerExpression::Version {
+                        key: uv_pep508::MarkerValueVersion::PythonVersion,
+                        specifier: VersionSpecifier::greater_than_equal_version(Version::new([
+                            u64::from(*major),
+                            u64::from(*minor),
+                        ])),
+                    })
+                } else {
+                    MarkerTree::expression(MarkerExpression::Version {
+                        key: uv_pep508::MarkerValueVersion::PythonVersion,
+                        specifier: VersionSpecifier::equals_star_version(Version::new([
+                            u64::from(*major),
+                            u64::from(*minor),
+                        ])),
+                    })
+                }
+            }
         };

         // Then, add implementation markers for implementation-specific tags
@@ -1123,6 +1148,20 @@ mod tests {
             "example-1.0-py311.py312-none-any.whl",
             "python_full_version >= '3.11' and python_full_version < '3.13'",
         );
+
+        // abi3 wheels: the python tag represents a minimum version, not an exact version.
+        assert_python_markers(
+            "example-1.0-cp39-abi3-any.whl",
+            "python_full_version >= '3.9' and platform_python_implementation == 'CPython'",
+        );
+        assert_python_markers(
+            "example-1.0-cp312-abi3-any.whl",
+            "python_full_version >= '3.12' and platform_python_implementation == 'CPython'",
+        );
+        assert_python_markers(
+            "example-1.0-cp3-abi3-any.whl",
+            "python_full_version >= '3' and platform_python_implementation == 'CPython'",
+        );
     }

     #[test]
@@ -1147,5 +1186,11 @@ mod tests {
             "example-1.0-py3-none-any.whl",
             "python_full_version >= '3' and python_full_version < '4'",
         );
+
+        // abi3 wheel: cp39-abi3 means CPython >= 3.9, combined with platform markers.
+        assert_implied_markers(
+            "example-1.0-cp39-abi3-manylinux_2_28_x86_64.whl",
+            "python_full_version >= '3.9' and platform_python_implementation == 'CPython' and sys_platform == 'linux' and platform_machine == 'x86_64'",
+        );
     }
 }
PATCH

echo "Patch applied successfully."
