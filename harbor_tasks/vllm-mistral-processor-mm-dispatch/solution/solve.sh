#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if image_processor is already a constructor param, patch is applied
if grep -q 'def __init__(.*image_processor.*MistralCommonImageProcessor' vllm/transformers_utils/processors/pixtral.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/vllm/model_executor/models/pixtral.py b/vllm/model_executor/models/pixtral.py
index 2dea34239387..0d891b8c9f20 100644
--- a/vllm/model_executor/models/pixtral.py
+++ b/vllm/model_executor/models/pixtral.py
@@ -61,7 +61,10 @@
 from vllm.sequence import IntermediateTensors
 from vllm.tokenizers import cached_tokenizer_from_config
 from vllm.tokenizers.mistral import MistralTokenizer
-from vllm.transformers_utils.processors.pixtral import MistralCommonPixtralProcessor
+from vllm.transformers_utils.processors.pixtral import (
+    MistralCommonImageProcessor,
+    MistralCommonPixtralProcessor,
+)
 from vllm.utils.collection_utils import is_list_of
 from vllm.utils.tensor_schema import TensorSchema, TensorShape

@@ -128,18 +131,20 @@ def get_tokenizer(self) -> MistralTokenizer:

         return tokenizer

+    def get_image_processor(self) -> MistralCommonImageProcessor:
+        return MistralCommonImageProcessor(self.get_tokenizer().instruct.mm_encoder)
+
     def get_hf_processor(self, **kwargs) -> MistralCommonPixtralProcessor:
-        return self.ctx.init_processor(
-            MistralCommonPixtralProcessor,
+        return MistralCommonPixtralProcessor(
             tokenizer=self.get_tokenizer(),
-            **kwargs,
+            image_processor=self.get_image_processor(),
         )

     def get_supported_mm_limits(self) -> Mapping[str, int | None]:
         return {"image": None}

     def get_image_size_with_most_features(self) -> ImageSize:
-        image_processor = self.get_hf_processor().image_processor
+        image_processor = self.get_image_processor()
         max_image_size = image_processor.mm_encoder.mm_config.max_image_size

         return ImageSize(width=max_image_size, height=max_image_size)
diff --git a/vllm/model_executor/models/voxtral.py b/vllm/model_executor/models/voxtral.py
index 30a2fa5512a8..d44960ca8117 100644
--- a/vllm/model_executor/models/voxtral.py
+++ b/vllm/model_executor/models/voxtral.py
@@ -55,7 +55,10 @@
 from vllm.sequence import IntermediateTensors
 from vllm.tokenizers import cached_tokenizer_from_config
 from vllm.tokenizers.mistral import MistralTokenizer
-from vllm.transformers_utils.processors.voxtral import MistralCommonVoxtralProcessor
+from vllm.transformers_utils.processors.voxtral import (
+    MistralCommonFeatureExtractor,
+    MistralCommonVoxtralProcessor,
+)
 from vllm.utils.collection_utils import is_list_of

 from .interfaces import SupportsLoRA, SupportsMultiModal, SupportsTranscription
@@ -84,15 +87,19 @@ def get_tokenizer(self) -> MistralTokenizer:

         return tokenizer

+    def get_feature_extractor(self) -> MistralCommonFeatureExtractor:
+        return MistralCommonFeatureExtractor(
+            self.get_tokenizer().instruct.audio_encoder
+        )
+
     def get_hf_processor(self, **kwargs) -> MistralCommonVoxtralProcessor:
-        return self.ctx.init_processor(
-            MistralCommonVoxtralProcessor,
+        return MistralCommonVoxtralProcessor(
             tokenizer=self.get_tokenizer(),
-            **kwargs,
+            feature_extractor=self.get_feature_extractor(),
         )

     def get_data_parser(self):
-        feature_extractor = self.get_hf_processor().feature_extractor
+        feature_extractor = self.get_feature_extractor()

         return MultiModalDataParser(
             target_sr=feature_extractor.sampling_rate,
@@ -114,7 +121,7 @@ def get_max_audio_tokens(self) -> int:
         return self.ctx.model_config.max_model_len

     def get_max_audio_array_len(self) -> int:
-        feature_extractor = self.get_hf_processor().feature_extractor
+        feature_extractor = self.get_feature_extractor()

         return self.get_max_audio_tokens() * int(
             feature_extractor.sampling_rate // feature_extractor.frame_rate
@@ -153,7 +160,7 @@ def get_dummy_processor_inputs(
         mm_data: MultiModalDataDict | None = None,
     ) -> ProcessorInputs:
         tokenizer = self.info.get_tokenizer()
-        feature_extractor = self.info.get_hf_processor().feature_extractor
+        feature_extractor = self.info.get_feature_extractor()

         dummy_text = self.get_dummy_text(mm_counts)
         dummy_mm_data = (
@@ -480,8 +487,10 @@ def get_num_audio_tokens(
         This is used for estimating the amount of processing for this audio.
         """
         tokenizer = cached_tokenizer_from_config(model_config)
-        adapter = MistralCommonVoxtralProcessor(tokenizer)
-        return adapter.feature_extractor.get_num_audio_tokens(
+        feature_extractor = MistralCommonFeatureExtractor(
+            tokenizer.instruct.audio_encoder
+        )
+        return feature_extractor.get_num_audio_tokens(
             int(audio_duration_s * stt_config.sample_rate)
         )

diff --git a/vllm/transformers_utils/processors/pixtral.py b/vllm/transformers_utils/processors/pixtral.py
index 39854d13257c..63c75151fcbd 100644
--- a/vllm/transformers_utils/processors/pixtral.py
+++ b/vllm/transformers_utils/processors/pixtral.py
@@ -50,16 +50,18 @@ def get_number_of_image_patches(
 class MistralCommonPixtralProcessor(ProcessorMixin):
     attributes = ["image_processor", "tokenizer"]

-    def __init__(self, tokenizer: MistralTokenizer) -> None:
+    def __init__(
+        self,
+        tokenizer: MistralTokenizer,
+        image_processor: MistralCommonImageProcessor,
+    ) -> None:
         self.tokenizer = tokenizer.transformers_tokenizer

         # Back-compatibility for Transformers v4
         if not hasattr(self.tokenizer, "init_kwargs"):
             self.tokenizer.init_kwargs = {}

-        self.image_processor = MistralCommonImageProcessor(
-            tokenizer.instruct.mm_encoder
-        )
+        self.image_processor = image_processor

         image_special_ids = self.image_processor.mm_encoder.special_ids
         self.image_break_id = image_special_ids.img_break
diff --git a/vllm/transformers_utils/processors/voxtral.py b/vllm/transformers_utils/processors/voxtral.py
index fc02e27de284..93f977291349 100644
--- a/vllm/transformers_utils/processors/voxtral.py
+++ b/vllm/transformers_utils/processors/voxtral.py
@@ -57,16 +57,18 @@ def get_num_audio_tokens(self, audio_length: int) -> int:
 class MistralCommonVoxtralProcessor(ProcessorMixin):
     attributes = ["feature_extractor", "tokenizer"]

-    def __init__(self, tokenizer: MistralTokenizer) -> None:
+    def __init__(
+        self,
+        tokenizer: MistralTokenizer,
+        feature_extractor: MistralCommonFeatureExtractor,
+    ) -> None:
         self.tokenizer = tokenizer.transformers_tokenizer

         # Back-compatibility for Transformers v4
         if not hasattr(self.tokenizer, "init_kwargs"):
             self.tokenizer.init_kwargs = {}

-        self.feature_extractor = MistralCommonFeatureExtractor(
-            tokenizer.instruct.audio_encoder
-        )
+        self.feature_extractor = feature_extractor

         audio_special_ids = self.feature_extractor.audio_encoder.special_ids
         self.audio_token_id = audio_special_ids.audio

PATCH

echo "Patch applied successfully."
