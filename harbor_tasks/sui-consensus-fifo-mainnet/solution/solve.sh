#!/bin/bash
set -e

cd /workspace/sui

# Idempotency check: already patched?
if ! grep -q '&& context.protocol_config.chain() != ChainType::Mainnet' consensus/core/src/authority_node.rs; then
    echo "Already patched or different code state"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | patch -p1
diff --git a/consensus/core/src/authority_node.rs b/consensus/core/src/authority_node.rs
index e83b7dc6895ee..da3020ef68087 100644
--- a/consensus/core/src/authority_node.rs
+++ b/consensus/core/src/authority_node.rs
@@ -3,10 +3,10 @@

 use std::{sync::Arc, time::Instant};

+use consensus_config::ConsensusProtocolConfig;
 use consensus_config::{
     AuthorityIndex, Committee, NetworkKeyPair, NetworkPublicKey, Parameters, ProtocolKeyPair,
 };
-use consensus_config::{ChainType, ConsensusProtocolConfig};
 use consensus_types::block::Round;
 use itertools::Itertools;
 use mysten_metrics::spawn_logged_monitored_task;
@@ -241,8 +241,7 @@ where
         let store_path = context.parameters.db_path.as_path().to_str().unwrap();
         let store = Arc::new(RocksDBStore::new(
             store_path,
-            context.parameters.use_fifo_compaction
-                && context.protocol_config.chain() != ChainType::Mainnet,
+            context.parameters.use_fifo_compaction,
         ));
         let dag_state = Arc::new(RwLock::new(DagState::new(context.clone(), store.clone())));
PATCH

echo "Patch applied successfully"
