#!/usr/bin/env bash
set -euo pipefail
cd /workspace/slime

# Idempotent: skip if already applied
if grep -q 'moe_token_dispatcher_type' slime/backends/megatron_utils/model_provider.py; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/backends/megatron_utils/model_provider.py b/slime/backends/megatron_utils/model_provider.py
index ba10c9956..6da7a6623 100644
--- a/slime/backends/megatron_utils/model_provider.py
+++ b/slime/backends/megatron_utils/model_provider.py
@@ -95,6 +95,8 @@ def wrapped_model_provider(
         provider.sequence_parallel = args.sequence_parallel
         provider.context_parallel_size = args.context_parallel_size
         provider.variable_seq_lengths = args.variable_seq_lengths
+        if hasattr(args, "moe_token_dispatcher_type"):
+            provider.moe_token_dispatcher_type = args.moe_token_dispatcher_type
         if getattr(args, "decoder_first_pipeline_num_layers", None) is not None:
             provider.num_layers_in_first_pipeline_stage = args.decoder_first_pipeline_num_layers
         if getattr(args, "decoder_last_pipeline_num_layers", None) is not None:

PATCH
