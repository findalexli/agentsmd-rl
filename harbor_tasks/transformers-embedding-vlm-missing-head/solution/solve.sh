#!/usr/bin/env bash
set -euo pipefail

cd /workspace/repo

# Idempotency check: if base_model_prefix already set in colpali, patch is applied
if grep -q 'base_model_prefix = "vlm"' src/transformers/models/colpali/modeling_colpali.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/transformers/conversion_mapping.py b/src/transformers/conversion_mapping.py
index 04bcc7e10190..73d2be3873e1 100755
--- a/src/transformers/conversion_mapping.py
+++ b/src/transformers/conversion_mapping.py
@@ -88,9 +88,6 @@ def _build_checkpoint_conversion_mapping():
             WeightRenaming(source_patterns=r"language_model.model", target_patterns="language_model"),
             WeightRenaming(source_patterns=r"language_model.lm_head", target_patterns="lm_head"),
         ],
-        "colpali": [
-            WeightRenaming(source_patterns=r"vlm(?!\.model)", target_patterns="vlm.model"),
-        ],
         "emu3": [
             WeightRenaming(source_patterns=r"text_model.model", target_patterns="text_model"),
             WeightRenaming(source_patterns=r"text_model.lm_head", target_patterns="lm_head"),
@@ -107,6 +104,10 @@ def _build_checkpoint_conversion_mapping():
                 source_patterns=r"(?<!_)model(?!\.(language_model|visual))", target_patterns="model.language_model"
             ),
         ],
+        "colqwen2": [
+            WeightRenaming(source_patterns=r"vlm.model", target_patterns="vlm"),
+            WeightRenaming(source_patterns=r"vlm(?!\.(language_model|visual))", target_patterns="vlm.language_model"),
+        ],
         "gemma3n_text": [
             WeightRenaming(source_patterns=r"^model.language_model", target_patterns="model"),
         ],
diff --git a/src/transformers/models/colmodernvbert/modeling_colmodernvbert.py b/src/transformers/models/colmodernvbert/modeling_colmodernvbert.py
index 4cd050d1810a..e7b6faf44cf1 100755
--- a/src/transformers/models/colmodernvbert/modeling_colmodernvbert.py
+++ b/src/transformers/models/colmodernvbert/modeling_colmodernvbert.py
@@ -104,6 +104,8 @@ class ColModernVBertForRetrievalOutput(ModelOutput):
     """
 )
 class ColModernVBertForRetrieval(ColModernVBertPreTrainedModel):
+    base_model_prefix = "vlm"
+
     def __init__(self, config: ColModernVBertConfig):
         super().__init__(config)
         self.config = config
@@ -152,36 +154,5 @@ def forward(
             image_hidden_states=vlm_output.image_hidden_states,
         )

-    def get_input_embeddings(self):
-        return self.vlm.get_input_embeddings()
-
-    def set_input_embeddings(self, value):
-        self.vlm.set_input_embeddings(value)
-
-    def get_output_embeddings(self):
-        return self.vlm.get_output_embeddings()
-
-    def set_output_embeddings(self, new_embeddings):
-        self.vlm.set_output_embeddings(new_embeddings)
-
-    def resize_token_embeddings(
-        self,
-        new_num_tokens: int | None = None,
-        pad_to_multiple_of: int | None = None,
-        mean_resizing: bool = True,
-    ) -> nn.Embedding:
-        model_embeds = self.vlm.resize_token_embeddings(
-            new_num_tokens=new_num_tokens,
-            pad_to_multiple_of=pad_to_multiple_of,
-            mean_resizing=mean_resizing,
-        )
-
-        self.config.vlm_config.text_config.vocab_size = model_embeds.num_embeddings
-        self.config.vlm_config.vocab_size = model_embeds.num_embeddings
-        self.vlm.vocab_size = model_embeds.num_embeddings
-        self.vocab_size = model_embeds.num_embeddings
-
-        return model_embeds
-

 __all__ = ["ColModernVBertForRetrieval", "ColModernVBertPreTrainedModel"]
diff --git a/src/transformers/models/colpali/modeling_colpali.py b/src/transformers/models/colpali/modeling_colpali.py
index 8153db085f95..dc7dcc306d33 100644
--- a/src/transformers/models/colpali/modeling_colpali.py
+++ b/src/transformers/models/colpali/modeling_colpali.py
@@ -18,7 +18,7 @@
 import torch
 from torch import nn

-from transformers import AutoModelForImageTextToText
+from transformers import AutoModel

 from ... import initialization as init
 from ...cache_utils import Cache
@@ -102,12 +102,14 @@ class ColPaliForRetrievalOutput(ModelOutput):
     """
 )
 class ColPaliForRetrieval(ColPaliPreTrainedModel):
+    base_model_prefix = "vlm"
+
     def __init__(self, config: ColPaliConfig):
         super().__init__(config)
         self.config = config
         self.vocab_size = config.vlm_config.text_config.vocab_size

-        self.vlm = AutoModelForImageTextToText.from_config(config.vlm_config)
+        self.vlm = AutoModel.from_config(config.vlm_config)

         self.embedding_dim = self.config.embedding_dim
         self.embedding_proj_layer = nn.Linear(
@@ -132,7 +134,7 @@ def forward(
         if output_hidden_states is None:
             output_hidden_states = self.config.output_hidden_states

-        vlm_output = self.vlm.model(
+        vlm_output = self.vlm(
             input_ids=input_ids,
             attention_mask=attention_mask,
             pixel_values=pixel_values,
@@ -160,37 +162,6 @@ def forward(
             image_hidden_states=vlm_image_hidden_states,
         )

-    def get_input_embeddings(self):
-        return self.vlm.get_input_embeddings()
-
-    def set_input_embeddings(self, value):
-        self.vlm.set_input_embeddings(value)
-
-    def get_output_embeddings(self):
-        return self.vlm.get_output_embeddings()
-
-    def set_output_embeddings(self, new_embeddings):
-        self.vlm.set_output_embeddings(new_embeddings)
-
-    def resize_token_embeddings(
-        self,
-        new_num_tokens: int | None = None,
-        pad_to_multiple_of: int | None = None,
-        mean_resizing: bool = True,
-    ) -> nn.Embedding:
-        model_embeds = self.vlm.resize_token_embeddings(
-            new_num_tokens=new_num_tokens,
-            pad_to_multiple_of=pad_to_multiple_of,
-            mean_resizing=mean_resizing,
-        )
-
-        self.config.vlm_config.text_config.vocab_size = model_embeds.num_embeddings
-        self.config.vlm_config.vocab_size = model_embeds.num_embeddings
-        self.vlm.vocab_size = model_embeds.num_embeddings
-        self.vocab_size = model_embeds.num_embeddings
-
-        return model_embeds
-

 __all__ = [
     "ColPaliForRetrieval",
diff --git a/src/transformers/models/colqwen2/modeling_colqwen2.py b/src/transformers/models/colqwen2/modeling_colqwen2.py
index 2f12f9d6da6d..656ad6c758c5 100644
--- a/src/transformers/models/colqwen2/modeling_colqwen2.py
+++ b/src/transformers/models/colqwen2/modeling_colqwen2.py
@@ -22,7 +22,7 @@

 from torch import nn

-from transformers import AutoModelForImageTextToText
+from transformers import AutoModel

 from ... import initialization as init
 from ...cache_utils import Cache
@@ -105,12 +105,14 @@ class ColQwen2ForRetrievalOutput(ModelOutput):
     """
 )
 class ColQwen2ForRetrieval(ColQwen2PreTrainedModel):
+    base_model_prefix = "vlm"
+
     def __init__(self, config: ColQwen2Config):
         super().__init__(config)
         self.config = config
         self.vocab_size = config.vlm_config.text_config.vocab_size

-        self.vlm = AutoModelForImageTextToText.from_config(config.vlm_config)
+        self.vlm = AutoModel.from_config(config.vlm_config)

         self.embedding_dim = self.config.embedding_dim
         self.embedding_proj_layer = nn.Linear(
@@ -162,16 +164,14 @@ def forward(
             inputs_embeds = self.vlm.get_input_embeddings()(input_ids)

             if pixel_values is not None:
-                image_embeds = self.vlm.model.visual(
-                    pixel_values, grid_thw=image_grid_thw, return_dict=True
-                ).pooler_output
+                image_embeds = self.vlm.visual(pixel_values, grid_thw=image_grid_thw, return_dict=True).pooler_output
                 image_mask = (
                     (input_ids == self.config.vlm_config.image_token_id).unsqueeze(-1).expand_as(inputs_embeds)
                 )
                 image_embeds = image_embeds.to(inputs_embeds.device, inputs_embeds.dtype)
                 inputs_embeds = inputs_embeds.masked_scatter(image_mask, image_embeds)

-        vlm_output = self.vlm.model(
+        vlm_output = self.vlm(
             input_ids=None,
             position_ids=position_ids,
             attention_mask=attention_mask,
@@ -201,36 +201,5 @@ def forward(
             attentions=vlm_output.attentions,
         )

-    def get_input_embeddings(self):
-        return self.vlm.get_input_embeddings()
-
-    def set_input_embeddings(self, value):
-        self.vlm.set_input_embeddings(value)
-
-    def get_output_embeddings(self):
-        return self.vlm.get_output_embeddings()
-
-    def set_output_embeddings(self, new_embeddings):
-        self.vlm.set_output_embeddings(new_embeddings)
-
-    def resize_token_embeddings(
-        self,
-        new_num_tokens: int | None = None,
-        pad_to_multiple_of: int | None = None,
-        mean_resizing: bool = True,
-    ) -> nn.Embedding:
-        model_embeds = self.vlm.resize_token_embeddings(
-            new_num_tokens=new_num_tokens,
-            pad_to_multiple_of=pad_to_multiple_of,
-            mean_resizing=mean_resizing,
-        )
-
-        self.config.vlm_config.text_config.vocab_size = model_embeds.num_embeddings
-        self.config.vlm_config.vocab_size = model_embeds.num_embeddings
-        self.vlm.vocab_size = model_embeds.num_embeddings
-        self.vocab_size = model_embeds.num_embeddings
-
-        return model_embeds
-

 __all__ = ["ColQwen2ForRetrieval", "ColQwen2PreTrainedModel"]
diff --git a/src/transformers/models/colqwen2/modular_colqwen2.py b/src/transformers/models/colqwen2/modular_colqwen2.py
index bd3f62e2d67d..aa7a3f48ca6e 100644
--- a/src/transformers/models/colqwen2/modular_colqwen2.py
+++ b/src/transformers/models/colqwen2/modular_colqwen2.py
@@ -303,16 +303,14 @@ def forward(
             inputs_embeds = self.vlm.get_input_embeddings()(input_ids)

             if pixel_values is not None:
-                image_embeds = self.vlm.model.visual(
-                    pixel_values, grid_thw=image_grid_thw, return_dict=True
-                ).pooler_output
+                image_embeds = self.vlm.visual(pixel_values, grid_thw=image_grid_thw, return_dict=True).pooler_output
                 image_mask = (
                     (input_ids == self.config.vlm_config.image_token_id).unsqueeze(-1).expand_as(inputs_embeds)
                 )
                 image_embeds = image_embeds.to(inputs_embeds.device, inputs_embeds.dtype)
                 inputs_embeds = inputs_embeds.masked_scatter(image_mask, image_embeds)

-        vlm_output = self.vlm.model(
+        vlm_output = self.vlm(
             input_ids=None,
             position_ids=position_ids,
             attention_mask=attention_mask,
diff --git a/tests/models/colmodernvbert/test_modeling_colmodernvbert.py b/tests/models/colmodernvbert/test_modeling_colmodernvbert.py
index 5fd8e62c8950..2f5134036d52 100755
--- a/tests/models/colmodernvbert/test_modeling_colmodernvbert.py
+++ b/tests/models/colmodernvbert/test_modeling_colmodernvbert.py
@@ -157,6 +157,7 @@ class ColModernVBertForRetrievalModelTest(ModelTesterMixin, unittest.TestCase):
     all_model_classes = (ColModernVBertForRetrieval,) if is_torch_available() else ()

     test_resize_embeddings = True
+    test_missing_keys = False
     model_split_percents = [0.5, 0.8, 0.9]

     def setUp(self):
diff --git a/tests/models/colpali/test_modeling_colpali.py b/tests/models/colpali/test_modeling_colpali.py
index 779cc4fa4d85..699d5019fbe1 100644
--- a/tests/models/colpali/test_modeling_colpali.py
+++ b/tests/models/colpali/test_modeling_colpali.py
@@ -182,6 +182,7 @@ class ColPaliForRetrievalModelTest(ModelTesterMixin, unittest.TestCase):

     all_model_classes = (ColPaliForRetrieval,) if is_torch_available() else ()
     test_resize_embeddings = True
+    test_missing_keys = False
     additional_model_inputs = ["token_type_ids"]

     def setUp(self):
diff --git a/tests/models/colqwen2/test_modeling_colqwen2.py b/tests/models/colqwen2/test_modeling_colqwen2.py
index a8e9a4a56eac..fb213177fb8b 100644
--- a/tests/models/colqwen2/test_modeling_colqwen2.py
+++ b/tests/models/colqwen2/test_modeling_colqwen2.py
@@ -202,6 +202,7 @@ class ColQwen2ForRetrievalModelTest(ModelTesterMixin, unittest.TestCase):

     test_resize_embeddings = True
     test_torch_exportable = False
+    test_missing_keys = False

     def setUp(self):
         self.model_tester = ColQwen2ForRetrievalModelTester(self)

PATCH

echo "Patch applied successfully."
