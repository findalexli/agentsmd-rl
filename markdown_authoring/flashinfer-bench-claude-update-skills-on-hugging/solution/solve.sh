#!/usr/bin/env bash
set -euo pipefail

cd /workspace/flashinfer-bench

# Idempotency guard
if grep -qF "**Note**: See [extract-kernel-definitions](../extract-kernel-definitions/SKILL.m" ".claude/skills/add-reference-tests/SKILL.md" && grep -qF "**IMPORTANT**: Always refer to the HuggingFace model page first (`https://huggin" ".claude/skills/extract-kernel-definitions/SKILL.md" && grep -qF "**IMPORTANT**: When creating definitions for new kernels, always refer to the Hu" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/add-reference-tests/SKILL.md b/.claude/skills/add-reference-tests/SKILL.md
@@ -67,14 +67,9 @@ Run `/clone-repos` first to set up the `tmp/` directory with SGLang and FlashInf
 
 For each definition, locate ground truth implementation using this priority order:
 
-#### For Model Constants: SGLang Model Config (Required)
-- **Location**: `tmp/sglang/python/sglang/srt/models/{model_name}.py`
-- **Use for**: Extracting and validating model-specific constant values
-- **Examples**:
-  - `num_attention_heads`, `num_key_value_heads`, `head_dim`
-  - `hidden_size`, `intermediate_size`
-  - `num_experts`, `topk`, `n_group`, `topk_group`
-- **Important**: Test constants must match SGLang model config
+#### For Model Constants: HuggingFace + SGLang (Required)
+
+**Note**: See [extract-kernel-definitions](../extract-kernel-definitions/SKILL.md#for-model-constants-huggingface--sglang-required) for detailed guidance on sourcing model constants from HuggingFace and SGLang.
 
 #### For Ground Truth Execution: FlashInfer API (Primary)
 - **When**: FlashInfer has the kernel implementation (MOST kernels)
diff --git a/.claude/skills/extract-kernel-definitions/SKILL.md b/.claude/skills/extract-kernel-definitions/SKILL.md
@@ -443,15 +443,11 @@ self.input_layernorm = RMSNorm(hidden_size, eps=rms_norm_eps)
 
 When extracting kernel definitions, use different sources for different purposes:
 
-### For Model Constants: SGLang Model Config (Required)
-- **Location**: `tmp/sglang/python/sglang/srt/models/{model_name}.py`
-- **Use for**: Extracting model-specific constant values
-- **Examples**:
-  - `num_attention_heads`, `num_key_value_heads`, `head_dim`
-  - `hidden_size`, `intermediate_size`
-  - `num_experts`, `topk`, `n_group`, `topk_group`
-  - `page_size` (from SGLang's paged attention configuration)
-- **Important**: Always align constants with SGLang's model config to ensure compatibility
+### For Model Constants: HuggingFace + SGLang (Required)
+
+**IMPORTANT**: Always refer to the HuggingFace model page first (`https://huggingface.co/{org}/{model-name}`) for authoritative model constants when creating definitions for new kernels. Download `config.json` from the model repo for values like `hidden_size`, `num_experts`, `topk`, etc.
+
+Use SGLang (`tmp/sglang/python/sglang/srt/models/{model_name}.py`) for runtime-specific constants like `page_size` and tensor parallel configurations (e.g. `num_attention_heads`, `num_local_experts`).
 
 ### For Reference `run()` Implementation: FlashInfer Unit Tests (PRIMARY - ALWAYS CHECK FIRST)
 - **When**: FlashInfer has a kernel implementation and corresponding unit test **(CHECK THIS FIRST)**
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -163,6 +163,8 @@ Add new model to `web/apps/web/data/models.ts`:
 
 #### 4. Map Modules to Definitions
 
+**IMPORTANT**: When creating definitions for new kernels, always refer to the HuggingFace model page (`https://huggingface.co/{org}/{model-name}`) to obtain authoritative model constants from `config.json`. Cross-reference with SGLang implementation for runtime-specific values like `page_size`.
+
 Associate each module with corresponding Definitions:
 
 - **Normalization layers**: `rmsnorm_h{hidden_size}`, `fused_add_rmsnorm_h{hidden_size}`
PATCH

echo "Gold patch applied."
