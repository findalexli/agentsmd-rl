#!/bin/bash
set -e

cd /workspace/sui

# Check if already patched (idempotency check)
if grep -q "min_tps: Option<f64>" crates/sui-benchmark/src/options.rs; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/crates/sui-benchmark/src/bin/stress.rs b/crates/sui-benchmark/src/bin/stress.rs
index da4fe7eab285..edfb48874fb9 100644
--- a/crates/sui-benchmark/src/bin/stress.rs
+++ b/crates/sui-benchmark/src/bin/stress.rs
@@ -54,6 +54,7 @@ use tokio::sync::Barrier;
 #[tokio::main]
 async fn main() -> Result<()> {
     let opts: Opts = Opts::parse();
+    let min_tps = opts.min_tps;

     // TODO: query the network for the current protocol version.
     let protocol_config = match opts.protocol_version {
@@ -202,6 +203,16 @@ async fn main() -> Result<()> {
                         let serialized = serde_json::to_string(&benchmark_stats)?;
                         std::fs::write(curr_benchmark_stats_path, serialized)?;
                     }
+
+                    if let Some(min_tps) = min_tps {
+                        let actual_tps = benchmark_stats.num_success_txes as f64
+                            / benchmark_stats.duration.as_secs_f64().max(1.0);
+                        if actual_tps < min_tps {
+                            return Err(anyhow::anyhow!(
+                                "TPS {actual_tps:.2} is below minimum threshold {min_tps}"
+                            ));
+                        }
+                    }
                 }
                 Err(e) => eprintln!("{e}"),
             },
diff --git a/crates/sui-benchmark/src/options.rs b/crates/sui-benchmark/src/options.rs
index 255ad3cfdc2a..8e58f08c8cbc 100644
--- a/crates/sui-benchmark/src/options.rs
+++ b/crates/sui-benchmark/src/options.rs
@@ -100,6 +100,11 @@ pub struct Opts {
     /// built at the same commit as the validators.
     #[clap(long, global = true)]
     pub protocol_version: Option<u64>,
+
+    /// If set, the stress binary will exit with a non-zero status code if the
+    /// achieved TPS is below this threshold.
+    #[clap(long, global = true)]
+    pub min_tps: Option<f64>,
 }

 #[derive(Debug, Clone, Parser, Eq, PartialEq, EnumString)]
PATCH

echo "Patch applied successfully!"
