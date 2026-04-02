#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if Qwen2VLTextConfig no longer has tie_word_embeddings field, already fixed
if ! grep -q 'tie_word_embeddings: bool = False' src/transformers/models/qwen2_vl/configuration_qwen2_vl.py; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/models/colmodernvbert/configuration_colmodernvbert.py b/src/transformers/models/colmodernvbert/configuration_colmodernvbert.py
index ad63892e890c..efa57dfc8640 100755
--- a/src/transformers/models/colmodernvbert/configuration_colmodernvbert.py
+++ b/src/transformers/models/colmodernvbert/configuration_colmodernvbert.py
@@ -72,9 +72,6 @@ def __post_init__(self, **kwargs):
         if not hasattr(self.vlm_config, "vocab_size"):
             self.vlm_config.vocab_size = self.vlm_config.get_text_config().vocab_size

-        # Move `tie_word_embeddings` under `vlm_config` for BC
-        if self.vlm_config.text_config.tie_word_embeddings and not self.vlm_config.tie_word_embeddings:
-            self.vlm_config.tie_word_embeddings = self.vlm_config.text_config.tie_word_embeddings
         super().__post_init__(**kwargs)

     def get_text_config(self, *args, **kwargs) -> PreTrainedConfig:
diff --git a/src/transformers/models/colqwen2/configuration_colqwen2.py b/src/transformers/models/colqwen2/configuration_colqwen2.py
index 19a4fc65b48c..ac9abcb5cfd9 100644
--- a/src/transformers/models/colqwen2/configuration_colqwen2.py
+++ b/src/transformers/models/colqwen2/configuration_colqwen2.py
@@ -56,9 +56,6 @@ def __post_init__(self, **kwargs):
         if not hasattr(self.vlm_config, "vocab_size"):
             self.vlm_config.vocab_size = self.vlm_config.get_text_config().vocab_size

-        # Move `tie_word_embeddings` under `vlm_config` for BC
-        if self.vlm_config.text_config.tie_word_embeddings and not self.vlm_config.tie_word_embeddings:
-            self.vlm_config.tie_word_embeddings = self.vlm_config.text_config.tie_word_embeddings
         super().__post_init__(**kwargs)

     def get_text_config(self, *args, **kwargs) -> PreTrainedConfig:
diff --git a/src/transformers/models/modernvbert/modeling_modernvbert.py b/src/transformers/models/modernvbert/modeling_modernvbert.py
index 7e58830ec1f6..b12a6a57f5f6 100755
--- a/src/transformers/models/modernvbert/modeling_modernvbert.py
+++ b/src/transformers/models/modernvbert/modeling_modernvbert.py
@@ -406,7 +406,7 @@ def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
 class ModernVBertForMaskedLM(ModernVBertPreTrainedModel):
     _tied_weights_keys = {"lm_head.weight": "model.text_model.embeddings.tok_embeddings.weight"}

-    def __init__(self, config):
+    def __init__(self, config: ModernVBertConfig):
         super().__init__(config)

         self.vocab_size = config.text_config.vocab_size
diff --git a/src/transformers/models/modernvbert/modular_modernvbert.py b/src/transformers/models/modernvbert/modular_modernvbert.py
index 3369bee145ec..e6eea13e7cfe 100755
--- a/src/transformers/models/modernvbert/modular_modernvbert.py
+++ b/src/transformers/models/modernvbert/modular_modernvbert.py
@@ -335,7 +335,7 @@ class ModernVBertPredictionHead(ModernBertPredictionHead):
 class ModernVBertForMaskedLM(ModernVBertPreTrainedModel):
     _tied_weights_keys = {"lm_head.weight": "model.text_model.embeddings.tok_embeddings.weight"}

-    def __init__(self, config):
+    def __init__(self, config: ModernVBertConfig):
         super().__init__(config)

         self.vocab_size = config.text_config.vocab_size
diff --git a/src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py b/src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py
index 09429d5b6ddb..911a5543ba48 100644
--- a/src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py
+++ b/src/transformers/models/qwen2_5_vl/configuration_qwen2_5_vl.py
@@ -123,7 +123,6 @@ class Qwen2_5_VLTextConfig(PreTrainedConfig):
     bos_token_id: int | None = 151643
     eos_token_id: int | list[int] | None = 151645
     pad_token_id: int | None = None
-    tie_word_embeddings: bool = False

     def __post_init__(self, **kwargs):
         self.sliding_window = self.sliding_window if self.use_sliding_window else None
diff --git a/src/transformers/models/qwen2_vl/configuration_qwen2_vl.py b/src/transformers/models/qwen2_vl/configuration_qwen2_vl.py
index 1b35a5d08e55..536bca3be654 100644
--- a/src/transformers/models/qwen2_vl/configuration_qwen2_vl.py
+++ b/src/transformers/models/qwen2_vl/configuration_qwen2_vl.py
@@ -100,7 +100,6 @@ class Qwen2VLTextConfig(PreTrainedConfig):
     bos_token_id: int | None = 151643
     eos_token_id: int | list[int] | None = 151645
     pad_token_id: int | None = None
-    tie_word_embeddings: bool = False

     def __post_init__(self, **kwargs):
         self.sliding_window = self.sliding_window if self.use_sliding_window else None

PATCH

echo "Patch applied successfully."
