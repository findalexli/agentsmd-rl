#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotency: check if already applied
if grep -q 'gc_threshold' python/sglang/srt/server_args.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/srt/entrypoints/engine.py b/python/sglang/srt/entrypoints/engine.py
index 35ebbf1bcc71..bf4b24fa05a2 100644
--- a/python/sglang/srt/entrypoints/engine.py
+++ b/python/sglang/srt/entrypoints/engine.py
@@ -616,6 +616,7 @@ def _launch_subprocesses(
         configure_logger(server_args)
         _set_envs_and_config(server_args)
         server_args.check_server_args()
+        _set_gc(server_args)

         # Allocate ports for inter-process communications
         if port_args is None:
@@ -1179,6 +1180,13 @@ def launch_phase_sigquit_handler(signum, frame):
     mp.set_start_method("spawn", force=True)


+def _set_gc(server_args: ServerArgs):
+    if gc_threshold := server_args.gc_threshold:
+        import gc
+
+        gc.set_threshold(*gc_threshold)
+
+
 def _wait_for_scheduler_ready(
     scheduler_pipe_readers: List,
     scheduler_procs: List,
diff --git a/python/sglang/srt/server_args.py b/python/sglang/srt/server_args.py
index c770f3d161f4..d9210c65647a 100644
--- a/python/sglang/srt/server_args.py
+++ b/python/sglang/srt/server_args.py
@@ -661,6 +661,7 @@ class ServerArgs:
     enable_deterministic_inference: bool = False
     rl_on_policy_target: Optional[str] = None
     enable_attn_tp_input_scattered: bool = False
+    gc_threshold: Optional[List[int]] = None
     # Context parallelism used in the long sequence prefill phase of DeepSeek v3.2
     enable_nsa_prefill_context_parallel: bool = False
     nsa_prefill_cp_mode: str = "round-robin-split"
@@ -5600,6 +5601,12 @@ def add_cli_args(parser: argparse.ArgumentParser):
             action="store_true",
             help="Enable fused moe triton and sum all reduce.",
         )
+        parser.add_argument(
+            "--gc-threshold",
+            type=int,
+            nargs="+",
+            help="Set the garbage collection thresholds (the collection frequency). Accepts 1 to 3 integers.",
+        )

         # Dynamic batch tokenizer
         parser.add_argument(
@@ -6116,6 +6123,12 @@ def check_server_args(self):
                 "When enabling two batch overlap, moe_a2a_backend cannot be 'none'."
             )

+        if self.gc_threshold:
+            if not (1 <= len(self.gc_threshold) <= 3):
+                raise ValueError(
+                    "When setting gc_threshold, it must contain 1 to 3 integers."
+                )
+
     def check_lora_server_args(self):
         assert self.max_loras_per_batch > 0, "max_loras_per_batch must be positive"

PATCH

echo "Patch applied successfully."
