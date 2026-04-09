#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'NoSupportedVersion' crates/ty_project/src/metadata/pyproject.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/crates/ty_project/src/metadata.rs b/crates/ty_project/src/metadata.rs
index b4b5339ef879f..abaeb405615bf 100644
--- a/crates/ty_project/src/metadata.rs
+++ b/crates/ty_project/src/metadata.rs
@@ -773,7 +773,7 @@ unclosed table, expected `]`
                 .unwrap_or_default()
                 .python_version
                 .as_deref(),
-            Some(&PythonVersion::from((3, 0)))
+            Some(&PythonVersion::PY37)
         );

         Ok(())
@@ -997,6 +997,66 @@ unclosed table, expected `]`
         Ok(())
     }

+    #[test]
+    fn requires_python_old_version_uses_lowest_supported_version() -> anyhow::Result<()> {
+        let system = TestSystem::default();
+        let root = SystemPathBuf::from("/app");
+
+        system
+            .memory_file_system()
+            .write_file_all(
+                root.join("pyproject.toml"),
+                r#"
+                [project]
+                requires-python = "==2.7"
+                "#,
+            )
+            .context("Failed to write file")?;
+
+        let root = ProjectMetadata::discover(&root, &system)?;
+
+        assert_eq!(
+            root.options
+                .environment
+                .unwrap_or_default()
+                .python_version
+                .as_deref(),
+            Some(&PythonVersion::PY37)
+        );
+
+        Ok(())
+    }
+
+    #[test]
+    fn requires_python_unsupported_future_version() -> anyhow::Result<()> {
+        let system = TestSystem::default();
+        let root = SystemPathBuf::from("/app");
+
+        system
+            .memory_file_system()
+            .write_file_all(
+                root.join("pyproject.toml"),
+                r#"
+                [project]
+                requires-python = "==44.44"
+                "#,
+            )
+            .context("Failed to write file")?;
+
+        let Err(error) = ProjectMetadata::discover(&root, &system) else {
+            return Err(anyhow!(
+                "Expected project discovery to fail because `requires-python` does not include a ty-supported version."
+            ));
+        };
+
+        assert_error_eq(
+            &error,
+            "Invalid `requires-python` version specifier (`/app/pyproject.toml`): value `==44.44` does not include any Python version supported by ty. Adjust `requires-python` to include a supported Python 3 version or specify `environment.python-version` explicitly.",
+        );
+
+        Ok(())
+    }
+
     #[track_caller]
     fn assert_error_eq(error: &ProjectMetadataError, message: &str) {
         assert_eq!(error.to_string().replace('\\', "/"), message);
diff --git a/crates/ty_project/src/metadata/pyproject.rs b/crates/ty_project/src/metadata/pyproject.rs
index ca25d05a617fb..d510309767530 100644
--- a/crates/ty_project/src/metadata/pyproject.rs
+++ b/crates/ty_project/src/metadata/pyproject.rs
@@ -114,10 +114,18 @@ impl Project {
         let minor =
             u8::try_from(minor).map_err(|_| ResolveRequiresPythonError::TooLargeMinor(minor))?;

+        let lower_bound = PythonVersion::from((major, minor));
+        let supported_version =
+            PythonVersion::iter().find(|supported_version| *supported_version >= lower_bound);
+
+        let Some(supported_version) = supported_version else {
+            return Err(ResolveRequiresPythonError::NoSupportedVersion(
+                requires_python.to_string(),
+            ));
+        };
+
         Ok(Some(
-            requires_python
-                .clone()
-                .map_value(|_| PythonVersion::from((major, minor))),
+            requires_python.clone().map_value(|_| supported_version),
         ))
     }
 }
@@ -132,6 +140,10 @@ pub enum ResolveRequiresPythonError {
         "value `{0}` does not contain a lower bound. Add a lower bound to indicate the minimum compatible Python version (e.g., `>=3.13`) or specify a version in `environment.python-version`."
     )]
     NoLowerBound(String),
+    #[error(
+        "value `{0}` does not include any Python version supported by ty. Adjust `requires-python` to include a supported Python 3 version or specify `environment.python-version` explicitly."
+    )]
+    NoSupportedVersion(String),
 }

 #[derive(Deserialize, Serialize, Debug, Clone, PartialEq, Eq)]

PATCH

echo "Patch applied successfully."
