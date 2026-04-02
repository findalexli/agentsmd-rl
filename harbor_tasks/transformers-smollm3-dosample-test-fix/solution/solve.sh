#!/usr/bin/env bash
set -euo pipefail

TARGET="/workspace/transformers/tests/models/smollm3/test_modeling_smollm3.py"

# Idempotency: check if already applied
if grep -q 'do_sample=False' "$TARGET" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

cd /workspace/transformers

git apply - <<'PATCH'
diff --git a/tests/models/smollm3/test_modeling_smollm3.py b/tests/models/smollm3/test_modeling_smollm3.py
index 7ed719e360eb..9ec8491560e1 100644
--- a/tests/models/smollm3/test_modeling_smollm3.py
+++ b/tests/models/smollm3/test_modeling_smollm3.py
@@ -100,14 +100,14 @@ def test_model_3b_logits(self):

     @slow
     def test_model_3b_generation(self):
-        EXPECTED_TEXT_COMPLETION = """Gravity is the force that pulls objects toward the center of the Earth. It is a force that is always present, even"""
+        EXPECTED_TEXT_COMPLETION = """Gravity is the force that pulls objects toward each other. It is the force that keeps your feet on the ground and makes"""
         prompt = "Gravity is the force"
         tokenizer = AutoTokenizer.from_pretrained(self.model_id)
         model = SmolLM3ForCausalLM.from_pretrained(self.model_id, device_map="auto")
         input_ids = tokenizer.encode(prompt, return_tensors="pt").to(model.model.embed_tokens.weight.device)

         # greedy generation outputs
-        generated_ids = model.generate(input_ids, max_new_tokens=20, temperature=0)
+        generated_ids = model.generate(input_ids, max_new_tokens=20, do_sample=False)
         text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
         self.assertEqual(EXPECTED_TEXT_COMPLETION, text)

@@ -130,14 +130,14 @@ def test_model_3b_long_prompt(self):
             attn_implementation="flash_attention_2",
         )
         input_ids = torch.tensor([input_ids]).to(model.model.embed_tokens.weight.device)
-        generated_ids = model.generate(input_ids, max_new_tokens=4, temperature=0)
+        generated_ids = model.generate(input_ids, max_new_tokens=4, do_sample=False)
         self.assertEqual(EXPECTED_OUTPUT_TOKEN_IDS, generated_ids[0][-2:].tolist())

         # Assisted generation
         assistant_model = model
         assistant_model.generation_config.num_assistant_tokens = 2
         assistant_model.generation_config.num_assistant_tokens_schedule = "constant"
-        generated_ids = model.generate(input_ids, max_new_tokens=4, temperature=0)
+        generated_ids = model.generate(input_ids, max_new_tokens=4, do_sample=False)
         self.assertEqual(EXPECTED_OUTPUT_TOKEN_IDS, generated_ids[0][-2:].tolist())

         del assistant_model

PATCH

echo "Patch applied successfully."
