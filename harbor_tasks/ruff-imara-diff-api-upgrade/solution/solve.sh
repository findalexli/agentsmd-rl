#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency: check if already applied
if grep -q 'imara-diff = { version = "0\.2' Cargo.toml 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/Cargo.toml b/Cargo.toml
index a6e14800235b97..ba8722ee68de04 100644
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -109,7 +109,7 @@ hashbrown = { version = "0.16.0", default-features = false, features = [
 ] }
 heck = "0.5.0"
 ignore = { version = "0.4.24" }
-imara-diff = { version = "0.1.5" }
+imara-diff = { version = "0.2.0" }
 imperative = { version = "1.0.4" }
 indexmap = { version = "2.6.0" }
 indicatif = { version = "0.18.0" }
diff --git a/crates/ruff_dev/src/format_dev.rs b/crates/ruff_dev/src/format_dev.rs
index 0f25e87bc3553e..63e7c5579353b1 100644
--- a/crates/ruff_dev/src/format_dev.rs
+++ b/crates/ruff_dev/src/format_dev.rs
@@ -11,9 +11,7 @@ use std::{fmt, fs, io, iter};

 use anyhow::{Context, Error, bail, format_err};
 use clap::{CommandFactory, FromArgMatches};
-use imara_diff::intern::InternedInput;
-use imara_diff::sink::Counter;
-use imara_diff::{Algorithm, diff};
+use imara_diff::{Algorithm, Diff, InternedInput};
 use indicatif::ProgressStyle;
 #[cfg_attr(feature = "singlethreaded", allow(unused_imports))]
 use rayon::iter::{IntoParallelIterator, ParallelIterator};
@@ -119,15 +117,17 @@ impl Statistics {
         } else {
             // `similar` was too slow (for some files >90% diffing instead of formatting)
             let input = InternedInput::new(black, ruff);
-            let changes = diff(Algorithm::Histogram, &input, Counter::default());
+            let changes = Diff::compute(Algorithm::Histogram, &input);
+            let removals = changes.count_removals();
+            let additions = changes.count_additions();
             assert_eq!(
-                input.before.len() - (changes.removals as usize),
-                input.after.len() - (changes.insertions as usize)
+                input.before.len() - (removals as usize),
+                input.after.len() - (additions as usize)
             );
             Self {
-                black_input: changes.removals,
-                ruff_output: changes.insertions,
-                intersection: u32::try_from(input.before.len()).unwrap() - changes.removals,
+                black_input: removals,
+                ruff_output: additions,
+                intersection: u32::try_from(input.before.len()).unwrap() - removals,
                 files_with_differences: 1,
             }
         }

PATCH

# Update Cargo.lock to resolve the new version
cargo update -p imara-diff
