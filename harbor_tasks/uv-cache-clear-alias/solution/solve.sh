#!/usr/bin/env bash
# Apply the gold fix from astral-sh/uv#18420: register `clear` as an alias of
# `cache clean` in the clap CLI definition. The patch is inlined as a HEREDOC
# to keep the oracle hermetic (no network fetch).
set -euo pipefail

cd /workspace/uv

# Idempotency: skip if the alias is already in place.
if grep -q '#\[command(alias = "clear")\]' crates/uv-cli/src/lib.rs; then
    echo "Patch already applied; skipping."
else
    git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/uv-cli/src/lib.rs b/crates/uv-cli/src/lib.rs
index c5c9a8b41e28c..516c9582dd8ef 100644
--- a/crates/uv-cli/src/lib.rs
+++ b/crates/uv-cli/src/lib.rs
@@ -865,6 +865,7 @@ pub struct CacheNamespace {
 #[derive(Subcommand)]
 pub enum CacheCommand {
     /// Clear the cache, removing all entries or those linked to specific packages.
+    #[command(alias = "clear")]
     Clean(CleanArgs),
     /// Prune all unreachable objects from the cache.
     Prune(PruneArgs),
PATCH
fi

# Incrementally rebuild the uv binary with the alias registered.
cargo build --bin uv -j 4
