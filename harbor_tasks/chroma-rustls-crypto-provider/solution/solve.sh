#!/bin/bash
set -e

cd /workspace/chroma

# Idempotency check: if fix is already applied, exit
if grep -q "install_rustls_crypto_provider" rust/tracing/src/init_tracer.rs; then
    echo "Fix already applied, exiting"
    exit 0
fi

# Apply the gold patch
patch -p1 << 'PATCH'
diff --git a/Cargo.lock b/Cargo.lock
index 16e56a0b33f..6eed9071389 100644
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -2142,6 +2142,7 @@ dependencies = [
  "opentelemetry 0.27.1",
  "opentelemetry-otlp",
  "opentelemetry_sdk",
+ "rustls 0.23.37",
  "serde",
  "serde_json",
  "tokio",
diff --git a/Cargo.toml b/Cargo.toml
index 598ba409304..04c0524ffb8 100644
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -78,6 +78,7 @@ usearch = "=2.23"
 faer = { version = "0.24.0", default-features = false, features = ["std", "rand"] }
 reqwest = { version = "0.13", features = ["rustls", "http2", "query"], default-features = false }
 random-port = "0.1.1"
+rustls = { version = "0.23.37", features = ["aws-lc-rs"] }
 ndarray = { version = "0.16.1", features = ["approx"] }
 humantime = { version = "2.2.0" }
 petgraph = { version = "0.8.1" }
diff --git a/rust/tracing/Cargo.toml b/rust/tracing/Cargo.toml
index 7ff63ee156a..270c4597b6e 100644
--- a/rust/tracing/Cargo.toml
+++ b/rust/tracing/Cargo.toml
@@ -25,6 +25,7 @@ axum = { workspace = true, optional = true }
 tower-http = { workspace = true, optional = true }
 futures = { workspace = true, optional = true }
 tokio = { workspace = true }
+rustls = { workspace = true }

 chroma-system = { workspace = true }

diff --git a/rust/tracing/src/init_tracer.rs b/rust/tracing/src/init_tracer.rs
index b48e70f9a7e..fd5677cdb69 100644
--- a/rust/tracing/src/init_tracer.rs
+++ b/rust/tracing/src/init_tracer.rs
@@ -17,6 +17,12 @@ use std::sync::OnceLock;

 static TOKIO_METRICS_INSTRUMENTS: OnceLock<TokioMetricsInstruments> = OnceLock::new();

+fn install_rustls_crypto_provider() {
+    // Multiple dependencies enable different rustls backends in this workspace.
+    // Install one explicitly before any TLS client config is built.
+    let _ = rustls::crypto::aws_lc_rs::default_provider().install_default();
+}
+
 #[allow(dead_code)]
 struct TokioMetricsInstruments {
     active_tasks_gauge: opentelemetry::metrics::ObservableGauge<u64>,
@@ -124,6 +130,8 @@ pub fn init_otel_layer(
     service_name: &String,
     otel_endpoint: &String,
 ) -> Box<dyn Layer<Registry> + Send + Sync> {
+    install_rustls_crypto_provider();
+
     tracing::info!(
         "Registering jaeger subscriber for {} at endpoint {}",
         service_name,
PATCH

echo "Fix applied successfully"
