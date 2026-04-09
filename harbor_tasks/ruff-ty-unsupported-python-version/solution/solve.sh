#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'deserialize_supported_python_version' crates/ty_project/src/metadata/options.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ty_project/src/metadata/options.rs b/crates/ty_project/src/metadata/options.rs
index c3cb7382f5ac7..4784ecd4e7cd3 100644
--- a/crates/ty_project/src/metadata/options.rs
+++ b/crates/ty_project/src/metadata/options.rs
@@ -20,7 +20,7 @@ use ruff_macros::{Combine, OptionsMetadata, RustDoc};
 use ruff_options_metadata::{OptionSet, OptionsMetadata, Visit};
 use ruff_python_ast::PythonVersion;
 use rustc_hash::FxHasher;
-use serde::{Deserialize, Serialize};
+use serde::{Deserialize, Deserializer, Serialize};
 use std::borrow::Cow;
 use std::cmp::Ordering;
 use std::fmt::{self, Debug, Display};
@@ -542,6 +542,29 @@ impl Options {
     }
 }

+fn deserialize_supported_python_version<'de, D>(
+    deserializer: D,
+) -> Result<Option<RangedValue<PythonVersion>>, D::Error>
+where
+    D: Deserializer<'de>,
+{
+    let python_version = Option::<RangedValue<PythonVersion>>::deserialize(deserializer)?;
+
+    if let Some(python_version) = &python_version
+        && !PythonVersion::iter().any(|supported_version| supported_version == **python_version)
+    {
+        return Err(serde::de::Error::custom(format!(
+            "unsupported value `{python_version}` for `python-version`; expected one of {}",
+            PythonVersion::iter()
+                .map(|version| format!("`{version}`"))
+                .collect::<Vec<_>>()
+                .join(", ")
+        )));
+    }
+
+    Ok(python_version)
+}
+
 /// Return the site-packages from the environment ty is installed in, as derived from ty's
 /// executable.
 ///
@@ -639,7 +662,11 @@ pub struct EnvironmentOptions {
     /// For some language features, ty can also understand conditionals based on comparisons
     /// with `sys.version_info`. These are commonly found in typeshed, for example,
     /// to reflect the differing contents of the standard library across Python versions.
-    #[serde(skip_serializing_if = "Option::is_none")]
+    #[serde(
+        default,
+        skip_serializing_if = "Option::is_none",
+        deserialize_with = "deserialize_supported_python_version"
+    )]
     #[option(
         default = r#""3.14""#,
         value_type = r#""3.7" | "3.8" | "3.9" | "3.10" | "3.11" | "3.12" | "3.13" | "3.14" | <major>.<minor>"#,

PATCH

echo "Patch applied successfully."
