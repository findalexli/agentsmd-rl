#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency check: if tokenizer_class field is already removed from PreTrainedConfig, skip
if ! grep -q 'tokenizer_class:.*PreTrainedTokenizerBase' src/transformers/configuration_utils.py 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/configuration_utils.py b/src/transformers/configuration_utils.py
index 211bfa95dee3..afcae7ddd75c 100755
--- a/src/transformers/configuration_utils.py
+++ b/src/transformers/configuration_utils.py
@@ -32,7 +32,6 @@
 from .generation.configuration_utils import GenerationConfig
 from .modeling_gguf_pytorch_utils import load_gguf_checkpoint
 from .modeling_rope_utils import RotaryEmbeddingConfigMixin
-from .tokenization_utils_base import PreTrainedTokenizerBase
 from .utils import (
     CONFIG_NAME,
     PushToHubMixin,
@@ -234,9 +233,6 @@ class PreTrainedConfig(PushToHubMixin, RotaryEmbeddingConfigMixin):
     label2id: dict[str, int] | dict[str, str] | None = None
     problem_type: Literal["regression", "single_label_classification", "multi_label_classification"] | None = None

-    # Tokenizer kwargs
-    tokenizer_class: str | PreTrainedTokenizerBase | None = None
-
     def __post_init__(self, **kwargs):
         # BC for the `torch_dtype` argument instead of the simpler `dtype`
         # Do not warn, as it would otherwise always be triggered since most configs on the hub have `torch_dtype`
diff --git a/src/transformers/models/mt5/configuration_mt5.py b/src/transformers/models/mt5/configuration_mt5.py
index 7dbc5bb83a56..72bae9c43951 100644
--- a/src/transformers/models/mt5/configuration_mt5.py
+++ b/src/transformers/models/mt5/configuration_mt5.py
@@ -29,8 +29,6 @@ class MT5Config(PreTrainedConfig):
         The maximum distance of the longer sequences for the bucket separation.
     feed_forward_proj (`str`, *optional*, defaults to `"gated-gelu"`):
         Type of feed forward layer to be used. Should be one of `"relu"` or `"gated-gelu"`.
-    tokenizer_class (`str`, *optional*, defaults to `"T5Tokenizer"`):
-        The tokenizer's class name.
     """

     model_type = "mt5"
@@ -57,7 +55,6 @@ class MT5Config(PreTrainedConfig):
     feed_forward_proj: str = "gated-gelu"
     is_encoder_decoder: bool = True
     use_cache: bool = True
-    tokenizer_class: str = "T5Tokenizer"
     tie_word_embeddings: bool = True
     bos_token_id: int | None = None
     pad_token_id: int | None = 0
diff --git a/src/transformers/models/umt5/configuration_umt5.py b/src/transformers/models/umt5/configuration_umt5.py
index 5c52f13e610e..5d78f4632dea 100644
--- a/src/transformers/models/umt5/configuration_umt5.py
+++ b/src/transformers/models/umt5/configuration_umt5.py
@@ -29,8 +29,6 @@ class UMT5Config(PreTrainedConfig):
         The maximum distance of the longer sequences for the bucket separation.
     feed_forward_proj (`str`, *optional*, defaults to `"gated-gelu"`):
         Type of feed forward layer to be used. Should be one of `"relu"` or `"gated-gelu"`.
-    tokenizer_class (`str`, *optional*, defaults to `"T5Tokenizer"`):
-        The tokenizer's class name
     """

     model_type = "umt5"
@@ -57,7 +55,6 @@ class UMT5Config(PreTrainedConfig):
     feed_forward_proj: str = "gated-gelu"
     is_encoder_decoder: bool = True
     use_cache: bool = True
-    tokenizer_class: str = "T5Tokenizer"
     pad_token_id: int | None = 0
     eos_token_id: int | list[int] | None = 1
     decoder_start_token_id: int | None = 0
diff --git a/tests/utils/test_configuration_utils.py b/tests/utils/test_configuration_utils.py
index f4b1041274d4..227c979990dd 100644
--- a/tests/utils/test_configuration_utils.py
+++ b/tests/utils/test_configuration_utils.py
@@ -146,7 +146,6 @@ def test_config_common_kwargs_is_complete(self):
             [
                 "transformers_version",
                 "is_encoder_decoder",
-                "tokenizer_class",
                 "_name_or_path",
                 "_commit_hash",
                 "_output_attentions",

PATCH

echo "Patch applied successfully."
