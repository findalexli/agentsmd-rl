#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency guard — if the gold patch is already applied, skip.
if grep -q "def prepare_decoder_input_ids_from_labels(self, labels: torch.Tensor):" \
       src/transformers/models/t5gemma2/modeling_t5gemma2.py 2>/dev/null; then
    echo "Patch already applied; skipping." >&2
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/transformers/models/t5gemma2/modeling_t5gemma2.py b/src/transformers/models/t5gemma2/modeling_t5gemma2.py
index 2e0dddc17876..90ab31a30665 100644
--- a/src/transformers/models/t5gemma2/modeling_t5gemma2.py
+++ b/src/transformers/models/t5gemma2/modeling_t5gemma2.py
@@ -706,7 +706,7 @@ def _init_weights(self, module):
                 init.copy_(getattr(module, f"{layer_type}_inv_freq"), curr_inv_freq)
                 init.copy_(getattr(module, f"{layer_type}_original_inv_freq"), curr_inv_freq)

-    def prepare_decoder_input_ids_from_labels(self, input_ids):
+    def prepare_decoder_input_ids_from_labels(self, labels: torch.Tensor):
         """
         Shifts input_ids to the right, prepends the decoder_start_token_id, and handles
         pad_token_id replacement for labels that were -100.
@@ -720,8 +720,8 @@ def prepare_decoder_input_ids_from_labels(self, input_ids):
             raise ValueError("self.model.config.decoder.bos_token_id has to be defined. ")

         # shift inputs to the right
-        shifted_input_ids = input_ids.new_zeros(input_ids.shape)
-        shifted_input_ids[..., 1:] = input_ids[..., :-1].clone()
+        shifted_input_ids = labels.new_zeros(labels.shape)
+        shifted_input_ids[..., 1:] = labels[..., :-1].clone()
         shifted_input_ids[..., 0] = decoder_start_token_id

         if pad_token_id is None:
diff --git a/src/transformers/models/t5gemma2/modular_t5gemma2.py b/src/transformers/models/t5gemma2/modular_t5gemma2.py
index 2f0f3720a7cd..53cf7518901a 100644
--- a/src/transformers/models/t5gemma2/modular_t5gemma2.py
+++ b/src/transformers/models/t5gemma2/modular_t5gemma2.py
@@ -513,7 +513,7 @@ def _init_weights(self, module):
                 init.copy_(getattr(module, f"{layer_type}_inv_freq"), curr_inv_freq)
                 init.copy_(getattr(module, f"{layer_type}_original_inv_freq"), curr_inv_freq)

-    def prepare_decoder_input_ids_from_labels(self, input_ids):
+    def prepare_decoder_input_ids_from_labels(self, labels: torch.Tensor):
         """
         Shifts input_ids to the right, prepends the decoder_start_token_id, and handles
         pad_token_id replacement for labels that were -100.
@@ -527,8 +527,8 @@ def prepare_decoder_input_ids_from_labels(self, input_ids):
             raise ValueError("self.model.config.decoder.bos_token_id has to be defined. ")

         # shift inputs to the right
-        shifted_input_ids = input_ids.new_zeros(input_ids.shape)
-        shifted_input_ids[..., 1:] = input_ids[..., :-1].clone()
+        shifted_input_ids = labels.new_zeros(labels.shape)
+        shifted_input_ids[..., 1:] = labels[..., :-1].clone()
         shifted_input_ids[..., 0] = decoder_start_token_id

         if pad_token_id is None:
PATCH

echo "Patch applied successfully." >&2
