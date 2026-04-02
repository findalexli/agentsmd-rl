#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency check: if the buggy bare-inputs pattern is gone, patch is already applied
if ! grep -q 'model\.generate(inputs,' tests/models/phi3/test_modeling_phi3.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/tests/models/phi3/test_modeling_phi3.py b/tests/models/phi3/test_modeling_phi3.py
index efcb22dc3137..71088134a63a 100644
--- a/tests/models/phi3/test_modeling_phi3.py
+++ b/tests/models/phi3/test_modeling_phi3.py
@@ -139,11 +139,11 @@ def test_phi3_mini_4k_instruct_generation(self):
         ]
         inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")

-        outputs = model.generate(inputs, max_new_tokens=32)
+        outputs = model.generate(**inputs, max_new_tokens=32)
         output_text = tokenizer.batch_decode(outputs)

         EXPECTED_OUTPUT = [
-            "<|system|> You are a helpful digital assistant. Please provide safe, ethical and accurate information to the user.<|end|><|user|> Can you provide ways to eat combinations of bananas and dragonfruits?<|end|><|assistant|> Certainly! Bananas and dragonfruits can be combined in various delicious ways. Here are some ideas for incorporating these fruits into your"
+            "<|system|> You are a helpful digital assistant. Please provide safe, ethical and accurate information to the user.<|end|><|user|> Can you provide ways to eat combinations of bananas and dragonfruits?<|end|><|assistant|> Certainly! Bananas and dragonfruits can be combined in various delicious and healthy ways. Here are some creative ideas to enjoy these"
         ]

         self.assertListEqual(output_text, EXPECTED_OUTPUT)
@@ -161,7 +161,7 @@ def test_phi3_mini_4k_instruct_with_static_cache(self):
         ]
         inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")

-        response_tokens = Phi3MiniWithStaticCache.generate(model, inputs, 64)
+        response_tokens = Phi3MiniWithStaticCache.generate(model, inputs["input_ids"], 64)

         output_text = tokenizer.batch_decode(torch.tensor([response_tokens], dtype=torch.long, device=torch_device))

@@ -207,7 +207,7 @@ def test_phi3_mini_128k_instruct_generation(self):
         ]
         inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")

-        outputs = model.generate(inputs, max_new_tokens=32)
+        outputs = model.generate(**inputs, max_new_tokens=32)
         output_text = tokenizer.batch_decode(outputs)

         EXPECTED_OUTPUT = [
@@ -229,7 +229,7 @@ def test_phi3_mini_128k_instruct_with_static_cache(self):
         ]
         inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")

-        response_tokens = Phi3MiniWithStaticCache.generate(model, inputs, 64)
+        response_tokens = Phi3MiniWithStaticCache.generate(model, inputs["input_ids"], 64)

         output_text = tokenizer.batch_decode(torch.tensor([response_tokens], dtype=torch.long, device=torch_device))

@@ -324,7 +324,7 @@ def test_phi3_mini_4k_sliding_window(self):
         outputs = model.generate(**inputs, max_new_tokens=100)
         output_text = tokenizer.batch_decode(outputs[:, inputs.input_ids.shape[1] :], skip_special_tokens=True)
         EXPECTED_OUTPUT = [
-            '1. Coq au Vin: Coq au Vin is a classic French dish that translates to "rooster in wine." The dish consists of chicken braised with wine, lardons, mushrooms, and garlic. It is a hearty and flavorful dish that is often served with potatoes or rice.\n\n            2. Boeuf Bourguignon: Boeuf Bourguignon is a traditional French beef stew that'
+            '1. Coq au Vin: Coq au Vin is a classic French dish that translates to "rooster in wine." The dish consists of chicken braised in red wine, typically Burgundy, along with mushrooms, onions, and sometimes bacon. The dish is known for its rich, savory flavor and tender chicken.\n\n            2. Boeuf Bourguignon: Boeuf Bourguignon is a hearty'
         ]

         self.assertListEqual(output_text, EXPECTED_OUTPUT)
diff --git a/tests/test_modeling_common.py b/tests/test_modeling_common.py
index e17511a5fc42..1aaf1bc69082 100755
--- a/tests/test_modeling_common.py
+++ b/tests/test_modeling_common.py
@@ -3612,6 +3612,7 @@ def test_sdpa_can_dispatch_on_flash(self):
                     "PaliGemma-like models currently (transformers==4.41.0) requires an attention_mask input"
                 )
             if config.model_type in [
+                "EvollaModel",
                 "modernbert",
                 "gemma3",
                 "t5gemma",
@@ -3623,6 +3624,9 @@ def test_sdpa_can_dispatch_on_flash(self):
                 "kosmos-2",
                 "mllama",
                 "lighton_ocr",
+                "parakeet_encoder",
+                "parakeet_ctc",
+                "pi0",
                 "pixtral",
                 "sam",
                 "sam_hq",

PATCH

echo "Patch applied successfully."
