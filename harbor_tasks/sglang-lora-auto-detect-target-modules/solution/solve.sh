#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotency: check if the fix is already applied
if grep -q "auto_detect_lora_target_modules" python/sglang/srt/lora/utils.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/srt/lora/lora_manager.py b/python/sglang/srt/lora/lora_manager.py
index 73f6bc23544e..7b222161f669 100644
--- a/python/sglang/srt/lora/lora_manager.py
+++ b/python/sglang/srt/lora/lora_manager.py
@@ -36,6 +36,7 @@
 from sglang.srt.lora.mem_pool import LoRAMemoryPool
 from sglang.srt.lora.utils import (
     LoRAType,
+    auto_detect_lora_target_modules,
     get_normalized_target_modules,
     get_target_module_name,
 )
@@ -424,9 +425,6 @@ def init_lora_shapes(

         for lora_id, config in self.configs.items():
             # Handle PEFT shorthand strings like "all-linear" or "all".
-            # These cannot be resolved to concrete module names without
-            # inspecting the base model, so we require the user to specify
-            # --lora-target-modules explicitly when such shorthands are used.
             if isinstance(config.target_modules, str):
                 if config.target_modules in ("all-linear", "all"):
                     if target_modules is not None:
@@ -434,14 +432,20 @@ def init_lora_shapes(
                         # per-adapter inference for this adapter.
                         continue
                     else:
-                        lora_name = self.lora_refs[lora_id].lora_name
-                        raise ValueError(
-                            f"LoRA adapter '{lora_name}' uses "
-                            f"target_modules='{config.target_modules}' which cannot "
-                            "be resolved automatically. Please explicitly specify "
-                            "--lora-target-modules during server startup. You can "
-                            "specify 'all' to enable all supported module types."
+                        # Resolve by scanning the base model for all
+                        # LoRA-compatible linear modules.
+                        adapter_target_modules = auto_detect_lora_target_modules(
+                            self.base_model
                         )
+                        logger.info(
+                            "LoRA adapter '%s' uses target_modules='%s'. "
+                            "Resolved to %s by inspecting the base model.",
+                            self.lora_refs[lora_id].lora_name,
+                            config.target_modules,
+                            sorted(adapter_target_modules),
+                        )
+                        self.target_modules.update(adapter_target_modules)
+                        continue
                 else:
                     raise ValueError(
                         f"SGLang does not recognize target_modules="
@@ -672,6 +676,8 @@ def init_lora_modules(self):
             # The module should be converted if it is included in target_names
             if module_name.split(".")[-1] in self.target_modules:
                 layer_id = get_layer_id(module_name)
+                if layer_id is None:
+                    continue
                 self.lora_modules[layer_id][module_name] = self.set_lora_module(
                     module_name, module
                 )
diff --git a/python/sglang/srt/lora/utils.py b/python/sglang/srt/lora/utils.py
index 45987d736d3c..1a12b1bd632d 100644
--- a/python/sglang/srt/lora/utils.py
+++ b/python/sglang/srt/lora/utils.py
@@ -113,13 +113,17 @@ def get_normalized_target_modules(
     Handles both base module names (e.g., "gate_proj") and prefixed module names (e.g., "feed_forward.gate_proj").

     Also handles PEFT shorthand strings like "all-linear" or "all" by returning
-    {"all"} as a sentinel value (the caller should check for "all" and fall
-    back to the CLI --lora-target-modules to determine the concrete module set).
+    {"all"} as a sentinel value.  Callers that need a concrete module set
+    should use :func:`auto_detect_lora_target_modules` to resolve the shorthand
+    against the loaded base model.
     """
-    # Handle PEFT shorthand strings — these cannot be resolved to concrete
-    # module names without inspecting the base model, so we return {"all"}
-    # and let the caller fall back to the CLI --lora-target-modules.
+    # Handle PEFT shorthand strings — return {"all"} as sentinel.
+    # Callers can resolve to concrete names via auto_detect_lora_target_modules().
     if isinstance(target_modules, str):
+        if target_modules not in ["all", "all-linear"]:
+            raise ValueError(
+                "Only 'all' or 'all-linear' can be used as the string for target module"
+            )
         return {"all"}

     params_mapping = {
@@ -175,6 +179,45 @@ def get_target_module_name(full_module_name: str, target_modules: Set[str]) -> s
 EMBEDDING_NAMES = ["embed_tokens", "lm_head"]
 ROW_PARALLELISM_LINEAR_LORA_NAMES = ["o_proj", "down_proj", "down_proj_moe"]

+# Normalized module names that the LoRA system fully supports
+# (i.e. get_hidden_dim, init_buffers, and init_lora_modules can handle them).
+_KNOWN_LORA_TARGET_MODULES = frozenset(
+    {
+        "qkv_proj",
+        "o_proj",
+        "gate_up_proj",
+        "down_proj",
+        "embed_tokens",
+        "lm_head",
+    }
+)
+
+
+def auto_detect_lora_target_modules(model: "torch.nn.Module") -> set:
+    """Discover LoRA-compatible modules by inspecting the base model.
+
+    Walks the model graph and returns the set of *normalized* target-module
+    names that (a) actually exist in the model and (b) the LoRA memory pool
+    can handle.  This is used to resolve PEFT shorthands like ``"all-linear"``
+    without requiring the user to enumerate modules on the CLI.
+    """
+    from sglang.srt.layers.linear import LinearBase
+    from sglang.srt.layers.moe.fused_moe_triton.layer import FusedMoE
+    from sglang.srt.layers.vocab_parallel_embedding import ParallelLMHead
+
+    raw_names: set = set()
+    for name, module in model.named_modules():
+        if isinstance(module, FusedMoE):
+            raw_names.add("gate_up_proj")
+            raw_names.add("down_proj")
+        elif isinstance(module, ParallelLMHead):
+            raw_names.add("lm_head")
+        elif isinstance(module, LinearBase):
+            raw_names.add(name.split(".")[-1])
+
+    normalized = get_normalized_target_modules(raw_names)
+    return normalized & _KNOWN_LORA_TARGET_MODULES
+

 def get_lm_head_lora_b_shard_size(output_dim: int, shard_indices=None) -> int:
     """Get the LoRA B output dimension for lm_head, accounting for TP.

PATCH

echo "Patch applied successfully."
