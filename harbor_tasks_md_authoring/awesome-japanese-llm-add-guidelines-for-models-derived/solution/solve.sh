#!/usr/bin/env bash
set -euo pipefail

cd /workspace/awesome-japanese-llm

# Idempotency guard
if grep -qF "- If the base model is a Japanese continual pre-training model (e.g., Swallow, E" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -127,6 +127,11 @@ When adding new models to the documentation:
      - **HuggingFace README mentions "Instruction Tuning", "SFT", "DPO", "Fine-tuning" only**: Post-training only
      - **HuggingFace README mentions "Pre-training", "Continual pre-training", "Additional pre-training"**: Continual pre-training
      - **Technical approaches like "Precise-tuning", "Pinpoint Tuning", "PEFT", "LoRA"**: Usually post-training methods
+   - **CRITICAL - Models derived from Japanese continual pre-training models**:
+     - If the base model is a Japanese continual pre-training model (e.g., Swallow, ELYZA, Nekomata, youko), the derived model belongs in the **継続事前学習 (Continual Pre-training)** section, NOT 事後学習のみ
+     - Example: A model fine-tuned on "Llama-3.1-Swallow-8B-Instruct" → place in 継続事前学習 → ドメイン特化型, because Swallow itself is a continual pre-training model
+     - This applies even if the derived model only does instruction tuning (SFT/DPO/LoRA) without additional pre-training
+     - **Base model column**: Record the **original architecture** (e.g., "Llama 3.1"), NOT the intermediate Japanese model name (e.g., NOT "Llama 3.1 Swallow")
    - **When in doubt**: Check the HuggingFace README technical details section first, then verify against press releases
 3. **Identify correct domain classification** - don't assume similar domains are the same (薬学 ≠ 医療)
    - **New model types**: If the model doesn't fit existing categories (e.g., music-language models vs speech-language models), create new sections following the established hierarchy
PATCH

echo "Gold patch applied."
