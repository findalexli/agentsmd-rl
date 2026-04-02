#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if Rocm72 already exists in backend.rs, patch is applied
if grep -q 'Rocm72' crates/uv-torch/src/backend.rs; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-torch/src/accelerator.rs b/crates/uv-torch/src/accelerator.rs
index 3f48103740bde..1b70b071405ad 100644
--- a/crates/uv-torch/src/accelerator.rs
+++ b/crates/uv-torch/src/accelerator.rs
@@ -295,6 +295,8 @@ pub enum AmdGpuArchitecture {
     Gfx1100,
     Gfx1101,
     Gfx1102,
+    Gfx1150,
+    Gfx1151,
     Gfx1200,
     Gfx1201,
 }
@@ -314,6 +316,8 @@ impl FromStr for AmdGpuArchitecture {
             "gfx1100" => Ok(Self::Gfx1100),
             "gfx1101" => Ok(Self::Gfx1101),
             "gfx1102" => Ok(Self::Gfx1102),
+            "gfx1150" => Ok(Self::Gfx1150),
+            "gfx1151" => Ok(Self::Gfx1151),
             "gfx1200" => Ok(Self::Gfx1200),
             "gfx1201" => Ok(Self::Gfx1201),
             _ => Err(AcceleratorError::UnknownAmdGpuArchitecture(s.to_string())),
@@ -334,6 +338,8 @@ impl std::fmt::Display for AmdGpuArchitecture {
             Self::Gfx1100 => write!(f, "gfx1100"),
             Self::Gfx1101 => write!(f, "gfx1101"),
             Self::Gfx1102 => write!(f, "gfx1102"),
+            Self::Gfx1150 => write!(f, "gfx1150"),
+            Self::Gfx1151 => write!(f, "gfx1151"),
             Self::Gfx1200 => write!(f, "gfx1200"),
             Self::Gfx1201 => write!(f, "gfx1201"),
         }
diff --git a/crates/uv-torch/src/backend.rs b/crates/uv-torch/src/backend.rs
index f5628e0db3568..75f1140314043 100644
--- a/crates/uv-torch/src/backend.rs
+++ b/crates/uv-torch/src/backend.rs
@@ -113,6 +113,10 @@ pub enum TorchMode {
     Cu90,
     /// Use the PyTorch index for CUDA 8.0.
     Cu80,
+    /// Use the PyTorch index for ROCm 7.2.
+    #[serde(rename = "rocm7.2")]
+    #[cfg_attr(feature = "clap", clap(name = "rocm7.2"))]
+    Rocm72,
     /// Use the PyTorch index for ROCm 7.1.
     #[serde(rename = "rocm7.1")]
     #[cfg_attr(feature = "clap", clap(name = "rocm7.1"))]
@@ -284,6 +288,7 @@ impl TorchStrategy {
             TorchMode::Cu91 => TorchBackend::Cu91,
             TorchMode::Cu90 => TorchBackend::Cu90,
             TorchMode::Cu80 => TorchBackend::Cu80,
+            TorchMode::Rocm72 => TorchBackend::Rocm72,
             TorchMode::Rocm71 => TorchBackend::Rocm71,
             TorchMode::Rocm70 => TorchBackend::Rocm70,
             TorchMode::Rocm64 => TorchBackend::Rocm64,
@@ -551,6 +556,7 @@ pub enum TorchBackend {
     Cu91,
     Cu90,
     Cu80,
+    Rocm72,
     Rocm71,
     Rocm70,
     Rocm64,
@@ -685,6 +691,10 @@ impl TorchBackend {
                 TorchSource::PyTorch => &PYTORCH_CU80_INDEX_URL,
                 TorchSource::Pyx => &PYX_CU80_INDEX_URL,
             },
+            Self::Rocm72 => match source {
+                TorchSource::PyTorch => &PYTORCH_ROCM72_INDEX_URL,
+                TorchSource::Pyx => &PYX_ROCM72_INDEX_URL,
+            },
             Self::Rocm71 => match source {
                 TorchSource::PyTorch => &PYTORCH_ROCM71_INDEX_URL,
                 TorchSource::Pyx => &PYX_ROCM71_INDEX_URL,
@@ -824,6 +834,7 @@ impl TorchBackend {
             Self::Cu91 => Some(Version::new([9, 1])),
             Self::Cu90 => Some(Version::new([9, 0])),
             Self::Cu80 => Some(Version::new([8, 0])),
+            Self::Rocm72 => None,
             Self::Rocm71 => None,
             Self::Rocm70 => None,
             Self::Rocm64 => None,
@@ -877,6 +888,7 @@ impl TorchBackend {
             Self::Cu91 => None,
             Self::Cu90 => None,
             Self::Cu80 => None,
+            Self::Rocm72 => Some(Version::new([7, 2])),
             Self::Rocm71 => Some(Version::new([7, 1])),
             Self::Rocm70 => Some(Version::new([7, 0])),
             Self::Rocm64 => Some(Version::new([6, 4])),
@@ -933,6 +945,7 @@ impl FromStr for TorchBackend {
             "cu91" => Ok(Self::Cu91),
             "cu90" => Ok(Self::Cu90),
             "cu80" => Ok(Self::Cu80),
+            "rocm7.2" => Ok(Self::Rocm72),
             "rocm7.1" => Ok(Self::Rocm71),
             "rocm7.0" => Ok(Self::Rocm70),
             "rocm6.4" => Ok(Self::Rocm64),
@@ -1050,9 +1063,24 @@ static WINDOWS_CUDA_VERSIONS: LazyLock<[(TorchBackend, Version); 26]> = LazyLock
 ///
 /// AMD also provides a compatibility matrix: <https://rocm.docs.amd.com/en/latest/compatibility/compatibility-matrix.html>;
 /// however, this list includes a broader array of GPUs than those in the matrix.
-static LINUX_AMD_GPU_DRIVERS: LazyLock<[(TorchBackend, AmdGpuArchitecture); 79]> =
+static LINUX_AMD_GPU_DRIVERS: LazyLock<[(TorchBackend, AmdGpuArchitecture); 93]> =
     LazyLock::new(|| {
         [
+            // ROCm 7.2
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx900),
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx906),
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx908),
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx90a),
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx942),
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx950),
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx1030),
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx1100),
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx1101),
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx1102),
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx1150),
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx1151),
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx1200),
+            (TorchBackend::Rocm72, AmdGpuArchitecture::Gfx1201),
             // ROCm 7.1
             (TorchBackend::Rocm71, AmdGpuArchitecture::Gfx900),
             (TorchBackend::Rocm71, AmdGpuArchitecture::Gfx906),
@@ -1197,6 +1225,8 @@ static PYTORCH_CU90_INDEX_URL: LazyLock<IndexUrl> =
     LazyLock::new(|| IndexUrl::from_str("https://download.pytorch.org/whl/cu90").unwrap());
 static PYTORCH_CU80_INDEX_URL: LazyLock<IndexUrl> =
     LazyLock::new(|| IndexUrl::from_str("https://download.pytorch.org/whl/cu80").unwrap());
+static PYTORCH_ROCM72_INDEX_URL: LazyLock<IndexUrl> =
+    LazyLock::new(|| IndexUrl::from_str("https://download.pytorch.org/whl/rocm7.2").unwrap());
 static PYTORCH_ROCM71_INDEX_URL: LazyLock<IndexUrl> =
     LazyLock::new(|| IndexUrl::from_str("https://download.pytorch.org/whl/rocm7.1").unwrap());
 static PYTORCH_ROCM70_INDEX_URL: LazyLock<IndexUrl> =
@@ -1351,6 +1381,10 @@ static PYX_CU80_INDEX_URL: LazyLock<IndexUrl> = LazyLock::new(|| {
     let api_base_url = &*PYX_API_BASE_URL;
     IndexUrl::from_str(&format!("{api_base_url}/simple/astral-sh/cu80")).unwrap()
 });
+static PYX_ROCM72_INDEX_URL: LazyLock<IndexUrl> = LazyLock::new(|| {
+    let api_base_url = &*PYX_API_BASE_URL;
+    IndexUrl::from_str(&format!("{api_base_url}/simple/astral-sh/rocm7.2")).unwrap()
+});
 static PYX_ROCM71_INDEX_URL: LazyLock<IndexUrl> = LazyLock::new(|| {
     let api_base_url = &*PYX_API_BASE_URL;
     IndexUrl::from_str(&format!("{api_base_url}/simple/astral-sh/rocm7.1")).unwrap()
diff --git a/uv.schema.json b/uv.schema.json
index fbc7d56fd9f8a..18272f5f91d0e 100644
--- a/uv.schema.json
+++ b/uv.schema.json
@@ -2404,6 +2404,11 @@
           "type": "string",
           "const": "cu80"
         },
+        {
+          "description": "Use the PyTorch index for ROCm 7.2.",
+          "type": "string",
+          "const": "rocm7.2"
+        },
         {
           "description": "Use the PyTorch index for ROCm 7.1.",
           "type": "string",

PATCH

echo "Patch applied successfully."
