#!/bin/bash
set -e

cd /workspace/sui

# Check if already patched (idempotency check)
if grep -q "min_tps" crates/sui-benchmark/src/options.rs 2>/dev/null; then
    echo "Patch already applied, exiting"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | patch -p1
From edfb48874fb9b6397734c21e8fd2a45fdf521d5d Mon Sep 17 00:00:00 2001
From: mwtian <81660174+mwtian@users.noreply.github.com>
Date: Tue, 8 Apr 2026 16:33:48 +0000
Subject: [PATCH 1/3] Add --min-tps flag to stress binary

---
 crates/sui-benchmark/src/bin/stress.rs | 11 +++++++++++
 crates/sui-benchmark/src/options.rs     |  5 +++++
 2 files changed, 16 insertions(+)

diff --git a/crates/sui-benchmark/src/bin/stress.rs b/crates/sui-benchmark/src/bin/stress.rs
index 1234567..abcdefg 100644
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
+                            return Err(anyhow!(
+                                "TPS {actual_tps:.2} is below minimum threshold {min_tps}"
+                            ));
+                        }
+                    }
                 }
                 Err(e) => eprintln!("{e}"),
             },
diff --git a/crates/sui-benchmark/src/options.rs b/crates/sui-benchmark/src/options.rs
index 1234567..abcdefg 100644
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

echo "Patch applied successfully"
