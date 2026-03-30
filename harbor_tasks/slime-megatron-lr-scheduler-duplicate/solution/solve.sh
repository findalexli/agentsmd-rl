#!/usr/bin/env bash
set -euo pipefail
cd /workspace/slime

# Idempotent: skip if already applied
if ! grep -q 'opt_param_scheduler.step' slime/backends/megatron_utils/model.py; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/slime/backends/megatron_utils/model.py b/slime/backends/megatron_utils/model.py
index 4995b948b..39f6125fc 100644
--- a/slime/backends/megatron_utils/model.py
+++ b/slime/backends/megatron_utils/model.py
@@ -782,6 +782,4 @@ def initialize_model_and_optimizer(
     )
     clear_memory()

-    opt_param_scheduler.step(increment=iteration * args.global_batch_size)
-
     return model, optimizer, opt_param_scheduler, iteration
PATCH
