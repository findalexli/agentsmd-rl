#!/bin/bash
set -e

cd /workspace/lancedb

# Idempotency check - if already patched, exit
if grep -q "lance_core::Error::io(format!" python/src/namespace.rs 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | patch -p1
diff --git a/Cargo.lock b/Cargo.lock
index 73d776d898..39c771c984 100644
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -3088,8 +3088,8 @@ checksum = "42703706b716c37f96a77aea830392ad231f44c9e9a67872fa5548707e11b11c"

 [[package]]
 name = "fsst"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow-array",
  "rand 0.9.2",
@@ -4260,8 +4260,8 @@ dependencies = [

 [[package]]
 name = "lance"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow",
  "arrow-arith",
@@ -4315,7 +4315,7 @@ dependencies = [
  "semver",
  "serde",
  "serde_json",
- "snafu",
+ "snafu 0.9.0",
  "tantivy",
  "tokio",
  "tokio-stream",
@@ -4327,8 +4327,8 @@ dependencies = [

 [[package]]
 name = "lance-arrow"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow-array",
  "arrow-buffer",
@@ -4338,6 +4338,7 @@ dependencies = [
  "arrow-schema",
  "arrow-select",
  "bytes",
+ "futures",
  "getrandom 0.2.16",
  "half",
  "jsonb",
@@ -4347,8 +4348,8 @@ dependencies = [

 [[package]]
 name = "lance-bitpacking"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrayref",
  "paste",
@@ -4357,8 +4358,8 @@ dependencies = [

 [[package]]
 name = "lance-core"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow-array",
  "arrow-buffer",
@@ -4384,7 +4385,7 @@ dependencies = [
  "rand 0.9.2",
  "roaring",
  "serde_json",
- "snafu",
+ "snafu 0.9.0",
  "tempfile",
  "tokio",
  "tokio-stream",
@@ -4395,8 +4396,8 @@ dependencies = [

 [[package]]
 name = "lance-datafusion"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow",
  "arrow-array",
@@ -4419,15 +4420,15 @@ dependencies = [
  "pin-project",
  "prost",
  "prost-build",
- "snafu",
+ "snafu 0.9.0",
  "tokio",
  "tracing",
 ]

 [[package]]
 name = "lance-datagen"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow",
  "arrow-array",
@@ -4445,8 +4446,8 @@ dependencies = [

 [[package]]
 name = "lance-encoding"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow-arith",
  "arrow-array",
@@ -4473,7 +4474,7 @@ dependencies = [
  "prost-build",
  "prost-types",
  "rand 0.9.2",
- "snafu",
+ "snafu 0.9.0",
  "strum",
  "tokio",
  "tracing",
@@ -4483,8 +4484,8 @@ dependencies = [

 [[package]]
 name = "lance-file"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow-arith",
  "arrow-array",
@@ -4509,15 +4510,15 @@ dependencies = [
  "prost",
  "prost-build",
  "prost-types",
- "snafu",
+ "snafu 0.9.0",
  "tokio",
  "tracing",
 ]

 [[package]]
 name = "lance-index"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow",
  "arrow-arith",
@@ -4569,7 +4570,7 @@ dependencies = [
  "serde",
  "serde_json",
  "smallvec",
- "snafu",
+ "snafu 0.9.0",
  "tantivy",
  "tempfile",
  "tokio",
@@ -4580,8 +4581,8 @@ dependencies = [

 [[package]]
 name = "lance-io"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow",
  "arrow-arith",
@@ -4613,7 +4614,7 @@ dependencies = [
  "prost",
  "rand 0.9.2",
  "serde",
- "snafu",
+ "snafu 0.9.0",
  "tempfile",
  "tokio",
  "tracing",
@@ -4622,8 +4623,8 @@ dependencies = [

 [[package]]
 name = "lance-linalg"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow-array",
  "arrow-buffer",
@@ -4639,21 +4640,21 @@ dependencies = [

 [[package]]
 name = "lance-namespace"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow",
  "async-trait",
  "bytes",
  "lance-core",
  "lance-namespace-reqwest-client",
- "snafu",
+ "snafu 0.9.0",
 ]

 [[package]]
 name = "lance-namespace-impls"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow",
  "arrow-ipc",
@@ -4675,7 +4676,7 @@ dependencies = [
  "reqwest",
  "serde",
  "serde_json",
- "snafu",
+ "snafu 0.9.0",
  "tokio",
  "tower",
  "tower-http 0.5.2",
@@ -4697,8 +4698,8 @@ dependencies = [

 [[package]]
 name = "lance-table"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow",
  "arrow-array",
@@ -4728,7 +4729,7 @@ dependencies = [
  "semver",
  "serde",
  "serde_json",
- "snafu",
+ "snafu 0.9.0",
  "tokio",
  "tracing",
  "url",
@@ -4737,8 +4738,8 @@ dependencies = [

 [[package]]
 name = "lance-testing"
-version = "3.0.0-rc.2"
-source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.2#3fb3e705b8a25ab1bb0fc9e1e0158e8a13356181"
+version = "3.0.0-rc.3"
+source = "git+https://github.com/lance-format/lance.git?tag=v3.0.0-rc.3#de393a26a068dd297929ca7d798e43dc31c57337"
 dependencies = [
  "arrow-array",
  "arrow-schema",
@@ -4819,7 +4820,7 @@ dependencies = [
  "serde",
  "serde_json",
  "serde_with",
- "snafu",
+ "snafu 0.8.9",
  "tempfile",
  "test-log",
  "tokenizers",
@@ -4869,7 +4870,7 @@ dependencies = [
  "pyo3-build-config",
  "serde",
  "serde_json",
- "snafu",
+ "snafu 0.8.9",
  "tokio",
 ]

@@ -7781,7 +7782,16 @@ version = "0.8.9"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "6e84b3f4eacbf3a1ce05eac6763b4d629d60cbc94d632e4092c54ade71f1e1a2"
 dependencies = [
- "snafu-derive",
+ "snafu-derive 0.8.9",
+]
+
+[[package]]
+name = "snafu"
+version = "0.9.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "d1d4bced6a69f90b2056c03dcff2c4737f98d6fb9e0853493996e1d253ca29c6"
+dependencies = [
+ "snafu-derive 0.9.0",
 ]

 [[package]]
@@ -7796,6 +7806,18 @@ dependencies = [
  "syn 2.0.114",
 ]

+[[package]]
+name = "snafu-derive"
+version = "0.9.0"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "54254b8531cafa275c5e096f62d48c81435d1015405a91198ddb11e967301d40"
+dependencies = [
+ "heck 0.4.1",
+ "proc-macro2",
+ "quote",
+ "syn 2.0.114",
+]
+
 [[package]]
 name = "socket2"
 version = "0.5.10"
diff --git a/Cargo.toml b/Cargo.toml
index 9ddddc4fb7..ce0d03de1c 100644
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -15,20 +15,20 @@ categories = ["database-implementations"]
 rust-version = "1.91.0"

 [workspace.dependencies]
-lance = { "version" = "=3.0.0-rc.2", default-features = false, "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
-lance-core = { "version" = "=3.0.0-rc.2", "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
-lance-datagen = { "version" = "=3.0.0-rc.2", "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
-lance-file = { "version" = "=3.0.0-rc.2", "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
-lance-io = { "version" = "=3.0.0-rc.2", default-features = false, "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
-lance-index = { "version" = "=3.0.0-rc.2", "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
-lance-linalg = { "version" = "=3.0.0-rc.2", "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
-lance-namespace = { "version" = "=3.0.0-rc.2", "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
-lance-namespace-impls = { "version" = "=3.0.0-rc.2", default-features = false, "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
-lance-table = { "version" = "=3.0.0-rc.2", "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
-lance-testing = { "version" = "=3.0.0-rc.2", "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
-lance-datafusion = { "version" = "=3.0.0-rc.2", "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
-lance-encoding = { "version" = "=3.0.0-rc.2", "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
-lance-arrow = { "version" = "=3.0.0-rc.2", "tag" = "v3.0.0-rc.2", "git" = "https://github.com/lance-format/lance.git" }
+lance = { "version" = "=3.0.0-rc.3", default-features = false, "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
+lance-core = { "version" = "=3.0.0-rc.3", "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
+lance-datagen = { "version" = "=3.0.0-rc.3", "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
+lance-file = { "version" = "=3.0.0-rc.3", "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
+lance-io = { "version" = "=3.0.0-rc.3", default-features = false, "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
+lance-index = { "version" = "=3.0.0-rc.3", "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
+lance-linalg = { "version" = "=3.0.0-rc.3", "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
+lance-namespace = { "version" = "=3.0.0-rc.3", "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
+lance-namespace-impls = { "version" = "=3.0.0-rc.3", default-features = false, "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
+lance-table = { "version" = "=3.0.0-rc.3", "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
+lance-testing = { "version" = "=3.0.0-rc.3", "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
+lance-datafusion = { "version" = "=3.0.0-rc.3", "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
+lance-encoding = { "version" = "=3.0.0-rc.3", "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
+lance-arrow = { "version" = "=3.0.0-rc.3", "tag" = "v3.0.0-rc.3", "git" = "https://github.com/lance-format/lance.git" }
 ahash = "0.8"
 # Note that this one does not include pyarrow
 arrow = { version = "57.2", optional = false }
diff --git a/python/src/namespace.rs b/python/src/namespace.rs
index c94a19a40b..b9b333cc57 100644
--- a/python/src/namespace.rs
+++ b/python/src/namespace.rs
@@ -96,10 +96,10 @@ where
     Resp: serde::de::DeserializeOwned + Send + 'static,
 {
     let request_json = serde_json::to_string(&request).map_err(|e| {
-        lance_core::Error::io(
-            format!("Failed to serialize request for {}: {}", method_name, e),
-            Default::default(),
-        )
+        lance_core::Error::io(format!(
+            "Failed to serialize request for {}: {}",
+            method_name, e
+        ))
     })?;

     let response_json = tokio::task::spawn_blocking(move || {
@@ -128,24 +128,14 @@ where
         })
     })
     .await
-    .map_err(|e| {
-        lance_core::Error::io(
-            format!("Task join error for {}: {}", method_name, e),
-            Default::default(),
-        )
-    })?
-    .map_err(|e: PyErr| {
-        lance_core::Error::io(
-            format!("Python error in {}: {}", method_name, e),
-            Default::default(),
-        )
-    })?;
+    .map_err(|e| lance_core::Error::io(format!("Task join error for {}: {}", method_name, e)))?
+    .map_err(|e: PyErr| lance_core::Error::io(format!("Python error in {}: {}", method_name, e)))?;

     serde_json::from_str(&response_json).map_err(|e| {
-        lance_core::Error::io(
-            format!("Failed to deserialize response from {}: {}", method_name, e),
-            Default::default(),
-        )
+        lance_core::Error::io(format!(
+            "Failed to deserialize response from {}: {}",
+            method_name, e
+        ))
     })
 }

@@ -159,10 +149,10 @@ where
     Req: serde::Serialize + Send + 'static,
 {
     let request_json = serde_json::to_string(&request).map_err(|e| {
-        lance_core::Error::io(
-            format!("Failed to serialize request for {}: {}", method_name, e),
-            Default::default(),
-        )
+        lance_core::Error::io(format!(
+            "Failed to serialize request for {}: {}",
+            method_name, e
+        ))
     })?;

     tokio::task::spawn_blocking(move || {
@@ -180,18 +170,8 @@ where
         })
     })
     .await
-    .map_err(|e| {
-        lance_core::Error::io(
-            format!("Task join error for {}: {}", method_name, e),
-            Default::default(),
-        )
-    })?
-    .map_err(|e: PyErr| {
-        lance_core::Error::io(
-            format!("Python error in {}: {}", method_name, e),
-            Default::default(),
-        )
-    })
+    .map_err(|e| lance_core::Error::io(format!("Task join error for {}: {}", method_name, e)))?
+    .map_err(|e: PyErr| lance_core::Error::io(format!("Python error in {}: {}", method_name, e)))
 }

 /// Helper for methods that return a primitive type
@@ -205,10 +185,10 @@ where
     Resp: for<'py> pyo3::FromPyObject<'py> + Send + 'static,
 {
     let request_json = serde_json::to_string(&request).map_err(|e| {
-        lance_core::Error::io(
-            format!("Failed to serialize request for {}: {}", method_name, e),
-            Default::default(),
-        )
+        lance_core::Error::io(format!(
+            "Failed to serialize request for {}: {}",
+            method_name, e
+        ))
     })?;

     tokio::task::spawn_blocking(move || {
@@ -227,18 +207,8 @@ where
         })
     })
     .await
-    .map_err(|e| {
-        lance_core::Error::io(
-            format!("Task join error for {}: {}", method_name, e),
-            Default::default(),
-        )
-    })?
-    .map_err(|e: PyErr| {
-        lance_core::Error::io(
-            format!("Python error in {}: {}", method_name, e),
-            Default::default(),
-        )
-    })
+    .map_err(|e| lance_core::Error::io(format!("Task join error for {}: {}", method_name, e)))?
+    .map_err(|e: PyErr| lance_core::Error::io(format!("Python error in {}: {}", method_name, e)))
 }

 /// Helper for methods that return Bytes
@@ -251,10 +221,10 @@ where
     Req: serde::Serialize + Send + 'static,
 {
     let request_json = serde_json::to_string(&request).map_err(|e| {
-        lance_core::Error::io(
-            format!("Failed to serialize request for {}: {}", method_name, e),
-            Default::default(),
-        )
+        lance_core::Error::io(format!(
+            "Failed to serialize request for {}: {}",
+            method_name, e
+        ))
     })?;

     tokio::task::spawn_blocking(move || {
@@ -273,18 +243,8 @@ where
         })
     })
     .await
-    .map_err(|e| {
-        lance_core::Error::io(
-            format!("Task join error for {}: {}", method_name, e),
-            Default::default(),
-        )
-    })?
-    .map_err(|e: PyErr| {
-        lance_core::Error::io(
-            format!("Python error in {}: {}", method_name, e),
-            Default::default(),
-        )
-    })
+    .map_err(|e| lance_core::Error::io(format!("Task join error for {}: {}", method_name, e)))?
+    .map_err(|e: PyErr| lance_core::Error::io(format!("Python error in {}: {}", method_name, e)))
 }

 /// Helper for methods that take request + data and return a response
@@ -299,10 +259,10 @@ where
     Resp: serde::de::DeserializeOwned + Send + 'static,
 {
     let request_json = serde_json::to_string(&request).map_err(|e| {
-        lance_core::Error::io(
-            format!("Failed to serialize request for {}: {}", method_name, e),
-            Default::default(),
-        )
+        lance_core::Error::io(format!(
+            "Failed to serialize request for {}: {}",
+            method_name, e
+        ))
     })?;

     let response_json = tokio::task::spawn_blocking(move || {
@@ -324,24 +284,14 @@ where
         })
     })
     .await
-    .map_err(|e| {
-        lance_core::Error::io(
-            format!("Task join error for {}: {}", method_name, e),
-            Default::default(),
-        )
-    })?
-    .map_err(|e: PyErr| {
-        lance_core::Error::io(
-            format!("Python error in {}: {}", method_name, e),
-            Default::default(),
-        )
-    })?;
+    .map_err(|e| lance_core::Error::io(format!("Task join error for {}: {}", method_name, e)))?
+    .map_err(|e: PyErr| lance_core::Error::io(format!("Python error in {}: {}", method_name, e)))?;

     serde_json::from_str(&response_json).map_err(|e| {
-        lance_core::Error::io(
-            format!("Failed to deserialize response from {}: {}", method_name, e),
-            Default::default(),
-        )
+        lance_core::Error::io(format!(
+            "Failed to deserialize response from {}: {}",
+            method_name, e
+        ))
     })
 }

diff --git a/python/src/storage_options.rs b/python/src/storage_options.rs
index d00c2aa16c..29ad9cebf1 100644
--- a/python/src/storage_options.rs
+++ b/python/src/storage_options.rs
@@ -66,13 +66,10 @@ impl StorageOptionsProvider for PyStorageOptionsProviderWrapper {
                     .inner
                     .bind(py)
                     .call_method0("fetch_storage_options")
-                    .map_err(|e| lance_core::Error::IO {
-                        source: Box::new(std::io::Error::other(format!(
-                            "Failed to call fetch_storage_options: {}",
-                            e
-                        ))),
-                        location: snafu::location!(),
-                    })?;
+                    .map_err(|e| lance_core::Error::io_source(Box::new(std::io::Error::other(format!(
+                        "Failed to call fetch_storage_options: {}",
+                        e
+                    )))))?;

                 // If result is None, return None
                 if result.is_none() {
@@ -81,26 +78,19 @@ impl StorageOptionsProvider for PyStorageOptionsProviderWrapper {

                 // Extract the result dict - should be a flat Map<String, String>
                 let result_dict = result.downcast::<PyDict>().map_err(|_| {
-                    lance_core::Error::InvalidInput {
-                        source: "fetch_storage_options() must return None or a dict of string key-value pairs".into(),
-                        location: snafu::location!(),
-                    }
+                    lance_core::Error::invalid_input(
+                        "fetch_storage_options() must return a dict of string key-value pairs or None",
+                    )
                 })?;

                 // Convert all entries to HashMap<String, String>
                 let mut storage_options = HashMap::new();
                 for (key, value) in result_dict.iter() {
                     let key_str: String = key.extract().map_err(|e| {
-                        lance_core::Error::InvalidInput {
-                            source: format!("Storage option key must be a string: {}", e).into(),
-                            location: snafu::location!(),
-                        }
+                        lance_core::Error::invalid_input(format!("Storage option key must be a string: {}", e))
                     })?;
                     let value_str: String = value.extract().map_err(|e| {
-                        lance_core::Error::InvalidInput {
-                            source: format!("Storage option value must be a string: {}", e).into(),
-                            location: snafu::location!(),
-                        }
+                        lance_core::Error::invalid_input(format!("Storage option value must be a string: {}", e))
                     })?;
                     storage_options.insert(key_str, value_str);
                 }
@@ -109,13 +99,10 @@ impl StorageOptionsProvider for PyStorageOptionsProviderWrapper {
             })
         }
         .await
-        .map_err(|e| lance_core::Error::IO {
-            source: Box::new(std::io::Error::other(format!(
-                "Task join error: {}",
-                e
-            ))),
-            location: snafu::location!(),
-        })?
+        .map_err(|e| lance_core::Error::io_source(Box::new(std::io::Error::other(format!(
+            "Task join error: {}",
+            e
+        )))))?
     }

     fn provider_id(&self) -> String {
diff --git a/rust/lancedb/src/database/namespace.rs b/rust/lancedb/src/database/namespace.rs
index 198b8c1868..2c5438e361 100644
--- a/rust/lancedb/src/database/namespace.rs
+++ b/rust/lancedb/src/database/namespace.rs
@@ -213,25 +213,18 @@ impl Database for LanceNamespaceDatabase {
             ..Default::default()
         };

-        let response = self
-            .namespace
-            .declare_table(declare_request)
-            .await
-            .map_err(|e| Error::Runtime {
-                message: format!("Failed to declare table: {}", e),
+        let (location, initial_storage_options, managed_versioning) = {
+            let response = self.namespace.declare_table(declare_request).await?;
+            let loc = response.location.ok_or_else(|| Error::Runtime {
+                message: "Table location is missing from declare_table response".to_string(),
             })?;
-
-        let location = response.location.ok_or_else(|| Error::Runtime {
-            message: "Table location is missing from declare_table response".to_string(),
-        })?;
-
-        // Use storage options from response, fall back to self.storage_options
-        let initial_storage_options = response
-            .storage_options
-            .or_else(|| Some(self.storage_options.clone()))
-            .filter(|o| !o.is_empty());
-
-        let managed_versioning = response.managed_versioning;
+            // Use storage options from response, fall back to self.storage_options
+            let opts = response
+                .storage_options
+                .or_else(|| Some(self.storage_options.clone()))
+                .filter(|o| !o.is_empty());
+            (loc, opts, response.managed_versioning)
+        };

         // Build write params with storage options and commit handler
         let mut params = request.write_options.lance_write_params.unwrap_or_default();
PATCH

echo "Patch applied successfully"
