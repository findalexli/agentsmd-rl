#!/usr/bin/env bash
set -euo pipefail

cd /workspace

# Idempotency check: if setup_hybrid_cp is already moved after setup_model, skip
if grep -q 'if parallel_dims.cp_enabled:' src/prime_rl/trainer/sft/train.py 2>/dev/null && \
   python3 -c "
import ast, sys
source = open('src/prime_rl/trainer/sft/train.py').read()
tree = ast.parse(source)
# Check that setup_hybrid_cp call comes after setup_model call
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'train':
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name) and child.func.id in ('setup_model', 'setup_hybrid_cp'):
                    calls.append((child.func.id, child.lineno))
                elif isinstance(child.func, ast.Attribute) and child.func.attr in ('setup_model', 'setup_hybrid_cp'):
                    calls.append((child.func.attr, child.lineno))
        model_line = next((l for n, l in calls if n == 'setup_model'), 0)
        hybrid_line = next((l for n, l in calls if n == 'setup_hybrid_cp'), 0)
        if hybrid_line > model_line > 0:
            sys.exit(0)
sys.exit(1)
" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/trainer/sft/train.py b/src/prime_rl/trainer/sft/train.py
index eabbc86cf7..dbbdeb290b 100644
--- a/src/prime_rl/trainer/sft/train.py
+++ b/src/prime_rl/trainer/sft/train.py
@@ -105,8 +105,6 @@ def train(config: SFTConfig):
         substitute_ring_attn(cp_group, heads_k_stride=1, attn_impl=config.model.attn)
         from prime_rl.utils.cp import setup_hybrid_cp

-        setup_hybrid_cp(model, cp_group, cp_rank, parallel_dims.cp)
-
     # Set up checkpoint manager
     logger.info(f"Initializing checkpoint managers ({config.ckpt})")
     ckpt_manager, weight_ckpt_manager = setup_ckpt_managers(config.output_dir, config.ckpt, config.model.lora)
@@ -125,6 +123,9 @@ def train(config: SFTConfig):
         config.model, parallel_dims, loading_from_ckpt_later, fused_cross_entropy=config.loss_impl == "liger_fused"
     )

+    if parallel_dims.cp_enabled:
+        setup_hybrid_cp(model, cp_group, cp_rank, parallel_dims.cp)
+
     if config.model.lora is not None:
         multi_run_manager = get_multi_run_manager()
         multi_run_manager.reset_run_parameters(0)

PATCH

echo "Patch applied successfully."
