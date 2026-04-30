#!/usr/bin/env bash
set -euo pipefail

cd /workspace/automodel

# Idempotency guard
if grep -qF ".claude/skills/developer-guide/SKILL.md" ".claude/skills/developer-guide/SKILL.md" && grep -qF ".claude/skills/distributed-training/SKILL.md" ".claude/skills/distributed-training/SKILL.md" && grep -qF ".claude/skills/launcher-config/SKILL.md" ".claude/skills/launcher-config/SKILL.md" && grep -qF "from nemo_automodel.components.models.<name>.layers import <Name>Attention as Ne" ".claude/skills/model-onboarding/SKILL.md" && grep -qF ".claude/skills/model-onboarding/llm-patterns.md" ".claude/skills/model-onboarding/llm-patterns.md" && grep -qF ".claude/skills/model-onboarding/moe-patterns.md" ".claude/skills/model-onboarding/moe-patterns.md" && grep -qF ".claude/skills/model-onboarding/vlm-patterns.md" ".claude/skills/model-onboarding/vlm-patterns.md" && grep -qF ".claude/skills/parity-testing/SKILL.md" ".claude/skills/parity-testing/SKILL.md" && grep -qF ".claude/skills/parity-testing/pitfalls.md" ".claude/skills/parity-testing/pitfalls.md" && grep -qF ".claude/skills/recipe-development/SKILL.md" ".claude/skills/recipe-development/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/developer-guide/SKILL.md b/.claude/skills/developer-guide/SKILL.md

diff --git a/.claude/skills/distributed-training/SKILL.md b/.claude/skills/distributed-training/SKILL.md

diff --git a/.claude/skills/launcher-config/SKILL.md b/.claude/skills/launcher-config/SKILL.md

diff --git a/.claude/skills/model-onboarding/SKILL.md b/.claude/skills/model-onboarding/SKILL.md
@@ -165,6 +165,33 @@ Before using full-size models, verify with a tiny config (1-2 layers, small hidd
 
 ## Phase 4: Tests
 
+### General testing rules
+
+- **Match the model's dtype.** Never invent or override the dtype in tests. If the
+  model runs in `bfloat16`, tests must also use `bfloat16`. Check the model's
+  `config.json` (`torch_dtype` field) or its default `model.dtype` and use that
+  everywhere -- model init, input tensors, reference tensors, and tolerance
+  thresholds. Using a different dtype (e.g., `float32` when the model uses
+  `bfloat16`) hides real precision issues and makes parity comparisons meaningless.
+
+- **Layer-rewrite equivalence tests.** Whenever you rewrite or replace a layer
+  (attention, MLP, normalization, RoPE, etc.) with a custom implementation, you
+  **must** add a unit test that checks numerical equivalence against the original
+  HuggingFace layer. Guidelines:
+  - Use a **realistically sized** layer config, not the absolute minimum. For
+    example, `hidden_size=256, num_attention_heads=8, num_key_value_heads=4` is
+    a reasonable choice. Extremely small dimensions (e.g., `hidden_size=8`) can
+    mask numerical divergence because there are too few elements for errors to
+    accumulate.
+  - Seed both the original and rewritten layer with identical weights (copy
+    `state_dict` from one to the other via the adapter if needed).
+  - Feed the same random input through both layers and assert
+    `torch.allclose(out_original, out_rewritten, atol=..., rtol=...)` with
+    tolerances appropriate for the dtype (`atol=1e-2, rtol=1e-2` for `bfloat16`;
+    `atol=1e-5, rtol=1e-5` for `float32`).
+  - Name the test `test_<layer>_equivalence` (e.g., `test_attention_equivalence`,
+    `test_mlp_equivalence`).
+
 ### 4.1 Unit tests
 
 Create `tests/unit_tests/models/<name>/` with:
@@ -200,7 +227,40 @@ def test_state_dict_roundtrip(model):
         assert torch.allclose(original_sd[key], restored_sd[key]), f"Mismatch at {key}"
 ```
 
-### 4.2 Functional tests
+### 4.2 Layer equivalence tests
+
+When a layer has been rewritten, add a test like:
+
+```python
+def test_attention_equivalence(tiny_config):
+    """Verify custom attention matches HF reference output."""
+    dtype = tiny_config.torch_dtype  # e.g. torch.bfloat16
+    torch.manual_seed(42)
+
+    # Instantiate original HF layer and custom NeMo layer
+    from transformers.models.<name>.modeling_<name> import <Name>Attention as HFAttention
+    from nemo_automodel.components.models.<name>.layers import <Name>Attention as NeMoAttention
+
+    hf_attn = HFAttention(tiny_config, layer_idx=0).to(dtype=dtype, device="cuda")
+    nemo_attn = NeMoAttention(tiny_config, layer_idx=0).to(dtype=dtype, device="cuda")
+
+    # Copy weights from HF to NeMo (via state_dict adapter or manual mapping)
+    # ... adapter.from_hf(hf_attn.state_dict()) ...
+
+    hidden = torch.randn(2, 32, tiny_config.hidden_size, dtype=dtype, device="cuda")
+    position_ids = torch.arange(32, device="cuda").unsqueeze(0).expand(2, -1)
+
+    with torch.no_grad():
+        hf_out = hf_attn(hidden, position_ids=position_ids)[0]
+        nemo_out = nemo_attn(hidden, position_ids=position_ids)[0]
+
+    atol, rtol = (1e-2, 1e-2) if dtype == torch.bfloat16 else (1e-5, 1e-5)
+    assert torch.allclose(hf_out, nemo_out, atol=atol, rtol=rtol), (
+        f"Max diff: {(hf_out - nemo_out).abs().max().item()}"
+    )
+```
+
+### 4.3 Functional tests
 
 Create a short training test (few steps) that verifies loss decreases:
 
@@ -238,6 +298,23 @@ Add fully commented example configs under `examples/`:
 
 ---
 
+## Phase 6: Parity Testing
+
+After implementation and unit tests are complete, run the full parity-testing
+workflow to verify that the new model produces numerically equivalent results to
+the reference HuggingFace implementation.
+
+**Read and follow the parity-testing skill** at
+`.claude/skills/parity-testing/SKILL.md`. It walks through three levels of
+comparison (state-dict round-trip, component-level parity, end-to-end forward
+pass) and provides debugging steps when a level fails.
+
+Do not skip this phase. A model that passes unit tests can still diverge from HF
+due to subtle weight-conversion bugs, backend differences, or RoPE mismatches
+that only surface in a full parity comparison.
+
+---
+
 ## Key Files Reference
 
 | File | Purpose |
@@ -273,6 +350,8 @@ Add fully commented example configs under `examples/`:
 - [ ] Created example YAML config
 - [ ] Verified model loads via `NeMoAutoModelForCausalLM.from_pretrained()`
 - [ ] Created unit tests (forward shape, state_dict round-trip)
+- [ ] Created layer equivalence tests for every rewritten layer (matching model dtype)
 - [ ] Created functional tests (training loss decreases)
 - [ ] Updated docs/model-coverage page
+- [ ] Ran parity-testing skill (state-dict round-trip, component parity, E2E forward pass)
 - [ ] Set `ModelClass = <Name>ForCausalLM` at module bottom
diff --git a/.claude/skills/model-onboarding/llm-patterns.md b/.claude/skills/model-onboarding/llm-patterns.md

diff --git a/.claude/skills/model-onboarding/moe-patterns.md b/.claude/skills/model-onboarding/moe-patterns.md

diff --git a/.claude/skills/model-onboarding/vlm-patterns.md b/.claude/skills/model-onboarding/vlm-patterns.md

diff --git a/.claude/skills/parity-testing/SKILL.md b/.claude/skills/parity-testing/SKILL.md

diff --git a/.claude/skills/parity-testing/pitfalls.md b/.claude/skills/parity-testing/pitfalls.md

diff --git a/.claude/skills/recipe-development/SKILL.md b/.claude/skills/recipe-development/SKILL.md

PATCH

echo "Gold patch applied."
