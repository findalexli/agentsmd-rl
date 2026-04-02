#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotency check: skip if the patch function already exists
if grep -q 'monkey_patch_dp_engine_core_pause_resume_deadlock' src/prime_rl/inference/patches.py; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/prime_rl/inference/patches.py b/src/prime_rl/inference/patches.py
index 3295dc5c37..480198e638 100644
--- a/src/prime_rl/inference/patches.py
+++ b/src/prime_rl/inference/patches.py
@@ -10,6 +10,7 @@ def transformers_v5_compat():
         Qwen3VLMoeTextConfig.tie_word_embeddings = False

     _patch_qwen35_lora()
+    monkey_patch_dp_engine_core_pause_resume_deadlock()


 def _patch_qwen35_lora():
@@ -712,3 +713,35 @@ def _apply_with_saved_kernel(self, layer, x, topk_weights, topk_ids, shared_expe
         self.base_layer._replace_quant_method(new_method)

     FusedMoEWithLoRA._inject_lora_into_fused_moe = _fixed_inject
+
+
+def monkey_patch_dp_engine_core_pause_resume_deadlock():
+    """Fix deadlock with pause/resume and collective_rpc in DP engine core.
+
+    When a request arrives for an already-completed wave while the scheduler is
+    paused, the unpatched code sends a start_wave notification that triggers
+    collective_rpc on other DP engines. But the paused engine can't participate
+    in the collective, causing a deadlock.
+
+    Fix: only send the start_wave notification when the scheduler is unpaused,
+    and explicitly set engines_running=True before notifying.
+
+    Upstream: https://github.com/vllm-project/vllm/pull/37024
+    """
+    from vllm.v1.core.sched.interface import PauseState
+    from vllm.v1.engine import EngineCoreOutputs
+    from vllm.v1.engine.core import DPEngineCoreProc, EngineCore
+    from vllm.v1.request import Request
+
+    _base_add_request = EngineCore.add_request
+
+    def _patched_add_request(self, request: Request, request_wave: int = 0):
+        _base_add_request(self, request, request_wave)
+        if self.has_coordinator and request_wave != self.current_wave:
+            if request_wave > self.current_wave:
+                self.current_wave = request_wave
+            elif not self.engines_running and self.scheduler.pause_state == PauseState.UNPAUSED:
+                self.engines_running = True
+                self.output_queue.put_nowait((-1, EngineCoreOutputs(start_wave=self.current_wave)))
+
+    DPEngineCoreProc.add_request = _patched_add_request

PATCH

echo "Patch applied successfully."
