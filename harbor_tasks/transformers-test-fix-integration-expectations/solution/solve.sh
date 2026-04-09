#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotent: skip if already applied (check for the distinctive Expectations usage)
if grep -q 'Expectations(' tests/models/qwen2/test_modeling_qwen2.py 2>/dev/null | grep -q 'get_expectation' 2>/dev/null || \
   grep -q 'from_pretrained("Qwen/Qwen2-0.5B"' tests/models/qwen2/test_modeling_qwen2.py 2>/dev/null | head -1; then
    # More specific check: see if the file has both 0.5B tokenizer AND Expectations usage
    if grep -A5 'def test_speculative_generation' tests/models/qwen2/test_modeling_qwen2.py | grep -q 'Qwen/Qwen2-0.5B' && \
       grep -A10 'def test_speculative_generation' tests/models/qwen2/test_modeling_qwen2.py | grep -q 'Expectations'; then
        echo "Patch already applied."
        exit 0
    fi
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/tests/models/qwen2/test_modeling_qwen2.py b/tests/models/qwen2/test_modeling_qwen2.py
index a2a00b5fe52a..48f1d95363c1 100644
--- a/tests/models/qwen2/test_modeling_qwen2.py
+++ b/tests/models/qwen2/test_modeling_qwen2.py
@@ -183,11 +183,13 @@ def test_model_450m_long_prompt_sdpa(self):

     @slow
     def test_speculative_generation(self):
-        EXPECTED_TEXT_COMPLETION = (
-            "My favourite condiment is 100% natural, organic, gluten-free, vegan, and vegetarian. I have been making"
-        )
+        EXPECTED_TEXT_COMPLETION = Expectations(
+            {
+                ("cuda", 8): "My favourite condiment is 100% real, organic, vegan and gluten free. I use it in my recipes and",
+            }
+        )  # fmt: skip
         prompt = "My favourite condiment is "
-        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-7B", use_fast=False)
+        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B", use_fast=False)
         model = Qwen2ForCausalLM.from_pretrained("Qwen/Qwen2-0.5B", device_map="auto", dtype=torch.float16)
         assistant_model = Qwen2ForCausalLM.from_pretrained("Qwen/Qwen2-0.5B", device_map="auto", dtype=torch.float16)
         input_ids = tokenizer.encode(prompt, return_tensors="pt").to(model.model.embed_tokens.weight.device)
diff --git a/tests/models/t5/test_modeling_t5.py b/tests/models/t5/test_modeling_t5.py
index d8eef68d7010..76499897fbf1 100644
--- a/tests/models/t5/test_modeling_t5.py
+++ b/tests/models/t5/test_modeling_t5.py
@@ -1428,14 +1428,14 @@ def test_compile_static_cache(self):

         # Dynamic Cache
         generated_ids = model.generate(**inputs, max_new_tokens=NUM_TOKENS_TO_GENERATE, do_sample=False)
-        dynamic_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
+        dynamic_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
         self.assertEqual(EXPECTED_TEXT_COMPLETION, dynamic_text)

         # Static Cache
         generated_ids = model.generate(
             **inputs, max_new_tokens=NUM_TOKENS_TO_GENERATE, do_sample=False, cache_implementation="static"
         )
-        static_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
+        static_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
         self.assertEqual(EXPECTED_TEXT_COMPLETION, static_text)

         # Static Cache + compile
@@ -1443,7 +1443,7 @@ def test_compile_static_cache(self):
         generated_ids = model.generate(
             **inputs, max_new_tokens=NUM_TOKENS_TO_GENERATE, do_sample=False, cache_implementation="static"
         )
-        static_compiled_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
+        static_compiled_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
         self.assertEqual(EXPECTED_TEXT_COMPLETION, static_compiled_text)

     @slow

PATCH

echo "Patch applied successfully."
