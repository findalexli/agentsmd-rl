# Agent Config Files for areal-vllm-pause-generation-native

Repo: inclusionAI/AReaL
Commit: 45e805ba8d274ec2c3cbb0699658449c2c6e163a
Files found: 44


---
## .agents/skills/add-archon-model/SKILL.md

```
   1 | ---
   2 | name: add-archon-model
   3 | description: Guide for adding a new model to the Archon engine. Use when user wants to add support for a new HuggingFace model architecture in ArchonEngine.
   4 | ---
   5 | 
   6 | # Add Archon Model
   7 | 
   8 | Add support for a new HuggingFace model architecture in the Archon training engine.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a model to Archon?"
  15 | - User wants to support a new model family (e.g., Llama, Mistral, DeepSeek) in
  16 |   ArchonEngine
  17 | - User mentions adding a new `ModelSpec` or model type for Archon
  18 | 
  19 | ## Prerequisites
  20 | 
  21 | Before starting, ensure:
  22 | 
  23 | - The target model is available on HuggingFace (has `config.json` with `model_type`)
  24 | - You know the HuggingFace model ID (e.g., `meta-llama/Llama-3-8B`)
  25 | - The model uses a standard transformer architecture (decoder-only)
  26 | 
  27 | ## Step-by-Step Guide
  28 | 
  29 | ### Step 1: Analyze the Target Model Architecture
  30 | 
  31 | Read the HuggingFace model's source code to extract key architecture information.
  32 | 
  33 | **Action**: Fetch and analyze the model's HuggingFace configuration and modeling files.
  34 | 
  35 | 1. Read the model's `config.json` (via `AutoConfig.from_pretrained`) to identify:
  36 | 
  37 |    - `model_type` string (this is the key used for registry lookup)
  38 |    - All architecture hyperparameters (hidden_size, num_layers, etc.)
  39 |    - Any model-specific fields (e.g., `qk_norm`, `attention_bias`, MoE fields)
  40 | 
  41 | 1. Read the HuggingFace `modeling_*.py` source to identify:
  42 | 
  43 |    - **Attention variant**: Does it have Q/K norm? Attention bias? Sliding window?
  44 |      Multi-latent attention?
  45 |    - **FFN variant**: SwiGLU (gate_proj + up_proj + down_proj)? GeGLU? Standard MLP?
  46 |    - **MoE support**: Does it have MoE layers? What router type? Shared experts?
  47 |    - **RoPE variant**: Standard RoPE? YaRN? NTK-aware scaling? What is the inv_freq
  48 |      formula?
  49 |    - **Normalization**: RMSNorm or LayerNorm? Pre-norm or post-norm? Elementwise affine?
  50 |    - **Weight tying**: Does `tie_word_embeddings` appear in config?
  51 |    - **State dict key names**: What are the HF weight key naming conventions?
  52 | 
  53 | 1. Summarize findings in a checklist like:
  54 | 
  55 | ```
  56 | Target model: <name>
  57 | HF model_type: "<model_type>" (and variants like "<model_type>_moe" if applicable)
  58 | Attention: [standard GQA / with QK norm / with bias / sliding window / ...]
  59 | FFN: [SwiGLU / GeGLU / standard MLP / ...]
  60 | MoE: [no / yes - num_experts, top_k, shared_experts]
  61 | RoPE: [standard / YaRN / NTK-aware / ...]
  62 | Norm: [RMSNorm / LayerNorm] with [pre-norm / post-norm]
  63 | Weight tying: [yes / no]
  64 | ```
  65 | 
  66 | ### Step 2: Select the Reference Model
  67 | 
  68 | Choose the closest existing implementation as a starting point:
  69 | 
  70 | | Target characteristics               | Reference | Why                                     |
  71 | | ------------------------------------ | --------- | --------------------------------------- |
  72 | | Dense-only, standard GQA, no QK norm | `qwen2`   | Simplest baseline, pure dense           |
  73 | | Has QK norm, or has MoE support      | `qwen3`   | Supports QK norm + MoE + shared experts |
  74 | 
  75 | **Action**: Copy the reference model directory as the starting point:
  76 | 
  77 | ```
  78 | areal/experimental/models/archon/<model>/
  79 |   __init__.py
  80 |   spec.py
  81 |   model/
  82 |     args.py
  83 |     model.py
  84 |     rope.py
  85 |     state_dict_adapter.py
  86 |   infra/
  87 |     parallelize.py
  88 | ```
  89 | 
  90 | ### Step 3: Implement `args.py`
  91 | 
  92 | Adapt `<Model>ModelArgs` to match the target model's HuggingFace config fields.
  93 | 
  94 | **Key changes from reference**:
  95 | 
  96 | 1. Update the `@dataclass` fields to match the target model's hyperparameters:
  97 | 
  98 |    - Field names should use Archon conventions (`dim`, `n_layers`, `n_heads`,
  99 |      `n_kv_heads`, `vocab_size`, `head_dim`, `hidden_dim`, `norm_eps`, `rope_theta`,
 100 |      etc.)
 101 |    - Default values should match the smallest variant of the target model
 102 |    - Add model-specific fields (e.g., `attention_bias`, `qk_norm`, `sliding_window`)
 103 | 
 104 | 1. Update `from_hf_config()` to correctly map HuggingFace config attributes:
 105 | 
 106 |    - Use `getattr(hf_config, "field_name", default)` for optional fields
 107 |    - Handle variant-specific fields (e.g., MoE fields only present in MoE variants)
 108 |    - The method must return an instance of the model args class
 109 | 
 110 | **Critical**: Verify every field mapping against the HF model's `config.json`. Incorrect
 111 | mappings here cause silent errors downstream.
 112 | 
 113 | **Base class contract** (`BaseModelArgs`):
 114 | 
 115 | ```python
 116 | @dataclass
 117 | class <Model>ModelArgs(BaseModelArgs):
 118 |     # ... model-specific fields ...
 119 | 
 120 |     @classmethod
 121 |     def from_hf_config(
 122 |         cls,
 123 |         hf_config: PretrainedConfig,
 124 |         is_critic: bool = False,
 125 |         **kwargs,
 126 |     ) -> <Model>ModelArgs:
 127 |         # Map HF config fields to Archon model args
 128 |         ...
 129 | ```
 130 | 
 131 | ### Step 4: Implement `model.py`
 132 | 
 133 | Adapt the model architecture to match the target model.
 134 | 
 135 | **Key components to adapt**:
 136 | 
 137 | 1. **Normalization** (`RMSNorm` or similar):
 138 | 
 139 |    - Check if `elementwise_affine` is configurable
 140 |    - Check the epsilon default value
 141 |    - If the model uses `LayerNorm`, implement accordingly
 142 | 
 143 | 1. **Attention** module:
 144 | 
 145 |    - Q/K/V projection: Check bias presence (`nn.Linear(..., bias=True/False)`)
 146 |    - QK norm: Add `q_norm`/`k_norm` if the model has them, remove if it doesn't
 147 |    - GQA: `n_kv_heads` \< `n_heads` for grouped-query attention
 148 |    - Ulysses SP: Keep the `set_cp_group` / `_sp_enabled` pattern from the reference
 149 |    - Output projection: Check bias presence
 150 | 
 151 | 1. **FeedForward** module:
 152 | 
 153 |    - SwiGLU: `w2(silu(w1(x)) * w3(x))` -- most common for modern LLMs
 154 |    - Check bias in linear layers
 155 |    - For MoE models: `MoE` module replaces `FeedForward` on designated layers
 156 | 
 157 | 1. **TransformerBlock**: Pre-norm (most modern LLMs) vs post-norm
 158 | 
 159 |    - MoE layer detection via `_is_moe_layer()` if applicable
 160 | 
 161 | 1. **Top-level Model** (`<Model>Model(BaseArchonModel)`):
 162 | 
 163 |    - `tok_embeddings`, `layers` (as `ModuleDict`), `norm`, `output`/`score`
 164 |    - `init_weights()`: Match initialization scheme from HF
 165 |    - `init_buffers()`: RoPE cache + MoE buffers
 166 |    - `forward()`: Must follow `BaseArchonModel` signature:
 167 |      `(tokens, positions, cu_seqlens, max_seqlen, tree_attn_meta=None) -> Tensor`
 168 | 
 169 | **Base class contract** (`BaseArchonModel`):
 170 | 
 171 | ```python
 172 | class <Model>Model(BaseArchonModel):
 173 |     def forward(self, tokens, positions, cu_seqlens, max_seqlen, tree_attn_meta=None) -> torch.Tensor: ...
 174 |     def init_weights(self) -> None: ...
 175 |     def init_buffers(self, buffer_device) -> None: ...
 176 | ```
 177 | 
 178 | ### Step 5: Implement `rope.py`
 179 | 
 180 | Handle the rotary position embedding variant.
 181 | 
 182 | **Options**:
 183 | 
 184 | 1. **Standard RoPE** (same as qwen2/qwen3): Re-export from qwen2:
 185 | 
 186 |    ```python
 187 |    from areal.experimental.models.archon.qwen2.model.rope import (
 188 |        apply_rotary_emb,
 189 |        precompute_rope_cache,
 190 |        repeat_kv,
 191 |        reshape_for_broadcast,
 192 |        rotate_half,
 193 |    )
 194 |    ```
 195 | 
 196 | 1. **Custom RoPE** (YaRN, NTK-aware, etc.): Implement custom `precompute_rope_cache()`
 197 |    and `apply_rotary_emb()` functions. The key difference is usually in how `inv_freq`
 198 |    is computed (scaling factors, interpolation, etc.).
 199 | 
 200 | ### Step 6: Implement `state_dict_adapter.py`
 201 | 
 202 | Map between HuggingFace and Archon weight key names.
 203 | 
 204 | **This is the most error-prone step.** The adapter must correctly handle:
 205 | 
 206 | 1. **Key name mapping** (`from_hf_map` dict):
 207 | 
 208 |    - Embedding: `model.embed_tokens.weight` -> `tok_embeddings.weight`
 209 |    - Attention: `model.layers.{}.self_attn.q_proj.weight` ->
 210 |      `layers.{}.attention.wq.weight`
 211 |    - FFN: `model.layers.{}.mlp.gate_proj.weight` -> `layers.{}.feed_forward.w1.weight`
 212 |    - Norms: `model.layers.{}.input_layernorm.weight` ->
 213 |      `layers.{}.attention_norm.weight`
 214 |    - Output: `lm_head.weight` -> `output.weight`
 215 |    - Skip keys (set to `None`): `rotary_emb.inv_freq` (computed at runtime)
 216 |    - Model-specific keys: bias terms, QK norm weights, etc.
 217 | 
 218 | 1. **Reverse mapping** (`to_hf_map`): Auto-generated from `from_hf_map`
 219 | 
 220 | 1. **MoE expert weights** (if applicable): 3D\<->2D conversion for expert weights. Copy
 221 |    the MoE handling from qwen3 if the model has MoE.
 222 | 
 223 | 1. **Weight tying**: Skip `output.weight` during `to_hf()` if `tie_word_embeddings=True`
 224 | 
 225 | **Verification approach**: After implementation, the adapter should satisfy:
 226 | 
 227 | ```python
 228 | # Roundtrip: archon -> hf -> archon preserves all keys
 229 | hf_sd = adapter.to_hf(archon_sd)
 230 | roundtrip_sd = adapter.from_hf(hf_sd)
 231 | assert set(roundtrip_sd.keys()) == set(archon_sd.keys())
 232 | ```
 233 | 
 234 | **Base class contract** (`BaseStateDictAdapter`):
 235 | 
 236 | ```python
 237 | class <Model>StateDictAdapter(BaseStateDictAdapter):
 238 |     def from_hf(self, hf_state_dict) -> dict[str, Any]: ...
 239 |     def to_hf(self, archon_state_dict) -> dict[str, Any]: ...
 240 |     def convert_single_to_hf(self, name, tensor) -> list[tuple[str, torch.Tensor]]: ...
 241 | ```
 242 | 
 243 | ### Step 7: Implement `parallelize.py`
 244 | 
 245 | Define the parallelization strategy for the model.
 246 | 
 247 | **The parallelize function** applies parallelism in this order:
 248 | 
 249 | 1. TP (Tensor Parallelism) -- shard attention/FFN across devices
 250 | 1. EP (Expert Parallelism) -- for MoE models only
 251 | 1. CP (Context Parallelism / Ulysses SP) -- sequence parallelism
 252 | 1. AC (Activation Checkpointing) -- memory optimization
 253 | 1. torch.compile -- compilation optimization
 254 | 1. FSDP (Fully Sharded Data Parallelism) -- data parallelism
 255 | 
 256 | **Key adaptations by model architecture**:
 257 | 
 258 | - **Attention with QK norm**: wq/wk use `use_local_output=False` (DTensor output for
 259 |   norm), add `SequenceParallel(sequence_dim=2)` for q_norm/k_norm
 260 | - **Attention without QK norm**: wq/wk/wv all use `use_local_output=True`
 261 | - **Attention with bias**: Bias terms follow the same parallel plan as their weights
 262 | - **MoE layers**: Separate TP plan for MoE input/output, router gate, and expert
 263 |   weights. Copy from qwen3's `apply_moe_ep_tp()` and `apply_non_moe_tp()`
 264 | - **Dense-only models**: Simpler plan without MoE handling. Copy from qwen2
 265 | 
 266 | **Function signature** (must match `ParallelizeFn` protocol):
 267 | 
 268 | ```python
 269 | def parallelize_<model>(
 270 |     model: nn.Module,
 271 |     parallel_dims: ArchonParallelDims,
 272 |     param_dtype: torch.dtype = torch.bfloat16,
 273 |     reduce_dtype: torch.dtype = torch.float32,
 274 |     loss_parallel: bool = True,
 275 |     cpu_offload: bool = False,
 276 |     reshard_after_forward_policy: str = "default",
 277 |     ac_config: ActivationCheckpointConfig | None = None,
 278 |     enable_compile: bool = True,
 279 | ) -> nn.Module:
 280 | ```
 281 | 
 282 | ### Step 8: Create `spec.py` and Register
 283 | 
 284 | Assemble the `ModelSpec` and register it.
 285 | 
 286 | ```python
 287 | from areal.experimental.models.archon.model_spec import ModelSpec, register_model_spec
 288 | from areal.experimental.models.archon.pipeline_parallel import pipeline_llm
 289 | from areal.experimental.models.archon.<model>.infra.parallelize import parallelize_<model>
 290 | from areal.experimental.models.archon.<model>.model.args import <Model>ModelArgs
 291 | from areal.experimental.models.archon.<model>.model.model import <Model>Model
 292 | from areal.experimental.models.archon.<model>.model.state_dict_adapter import (
 293 |     <Model>StateDictAdapter,
 294 | )
 295 | 
 296 | <MODEL>_SPEC = ModelSpec(
 297 |     name="<Model>",
 298 |     model_class=<Model>Model,
 299 |     model_args_class=<Model>ModelArgs,
 300 |     state_dict_adapter_class=<Model>StateDictAdapter,
 301 |     parallelize_fn=parallelize_<model>,
 302 |     supported_model_types=frozenset({"<model_type>"}),  # From HF config.json
 303 |     pipelining_fn=pipeline_llm,
 304 | )
 305 | 
 306 | # Auto-register when module is imported
 307 | register_model_spec(<MODEL>_SPEC)
 308 | 
 309 | __all__ = ["<MODEL>_SPEC"]
 310 | ```
 311 | 
 312 | **Note**: `supported_model_types` should include all HF `model_type` strings that this
 313 | implementation handles (e.g., `{"qwen3", "qwen3_moe"}` for Qwen3).
 314 | 
 315 | ### Step 9: Register in `__init__.py`
 316 | 
 317 | Add the import to `areal/experimental/models/archon/__init__.py`:
 318 | 
 319 | ```python
 320 | from areal.experimental.models.archon.<model> import spec as <model>_spec  # noqa: F401
 321 | ```
 322 | 
 323 | This triggers auto-registration when the module is imported.
 324 | 
 325 | ### Step 10: Verify and Test
 326 | 
 327 | Verification should be done in stages, adapting based on available hardware and the test
 328 | patterns in `tests/experimental/archon/`.
 329 | 
 330 | **Before writing tests**, examine the existing test files to understand current
 331 | patterns:
 332 | 
 333 | ```
 334 | tests/experimental/archon/
 335 |   conftest.py             -- Pytest configuration (version checks)
 336 |   utils.py                -- Shared utilities (model loading, comparison)
 337 |   test_qwen3_args.py      -- Args unit tests (CPU-only)
 338 |   test_state_dict_adapter.py  -- State dict roundtrip tests
 339 |   test_weight_sync.py     -- Weight completeness tests (meta device)
 340 |   test_forward.py         -- Forward precision comparison (single GPU)
 341 |   ...
 342 | ```
 343 | 
 344 | **Test stages** (write tests appropriate for the model's complexity):
 345 | 
 346 | #### Stage 1: Args Tests (CPU-only, always write these)
 347 | 
 348 | Test `from_hf_config()` with mock HuggingFace configs:
 349 | 
 350 | ```python
 351 | # Pattern: Create mock PretrainedConfig, verify args mapping
 352 | from unittest.mock import MagicMock
 353 | 
 354 | def test_args_from_hf_config():
 355 |     hf_config = MagicMock()
 356 |     hf_config.hidden_size = 4096
 357 |     hf_config.num_hidden_layers = 32
 358 |     # ... set all required fields
 359 |     args = <Model>ModelArgs.from_hf_config(hf_config)
 360 |     assert args.dim == 4096
 361 |     assert args.n_layers == 32
 362 | ```
 363 | 
 364 | #### Stage 2: State Dict Adapter Tests (CPU-only)
 365 | 
 366 | Test key mapping roundtrip:
 367 | 
 368 | ```python
 369 | def test_state_dict_roundtrip():
 370 |     # Create adapter with mock config
 371 |     adapter = <Model>StateDictAdapter(mock_config)
 372 |     # Create fake archon state dict with expected keys
 373 |     archon_sd = {"tok_embeddings.weight": torch.randn(vocab, dim), ...}
 374 |     # Roundtrip
 375 |     hf_sd = adapter.to_hf(archon_sd)
 376 |     roundtrip = adapter.from_hf(hf_sd)
 377 |     assert set(roundtrip.keys()) == set(archon_sd.keys())
 378 | ```
 379 | 
 380 | #### Stage 3: Weight Completeness (meta device, CPU-only)
 381 | 
 382 | Verify all model parameters have HF mappings:
 383 | 
 384 | ```python
 385 | def test_weight_completeness():
 386 |     # Create model on meta device
 387 |     with torch.device("meta"):
 388 |         model = <Model>Model(args)
 389 |     adapter = <Model>StateDictAdapter(hf_config)
 390 |     # Check every archon param has a HF mapping
 391 |     for name, _ in model.named_parameters():
 392 |         hf_pairs = adapter.convert_single_to_hf(name, torch.empty(0))
 393 |         assert len(hf_pairs) > 0, f"No HF mapping for {name}"
 394 | ```
 395 | 
 396 | #### Stage 4: Forward Precision (single GPU, if available)
 397 | 
 398 | Compare Archon model output against HuggingFace reference:
 399 | 
 400 | ```python
 401 | @pytest.mark.skipif(not torch.cuda.is_available(), reason="Requires CUDA")
 402 | def test_forward_matches_hf():
 403 |     # Load both HF and Archon models
 404 |     # Run forward on same input
 405 |     # Compare logits within tolerance
 406 | ```
 407 | 
 408 | **Important**: Do NOT hardcode the test categories. Inspect the existing test files in
 409 | `tests/experimental/archon/` and follow the same patterns, fixtures, and markers. Adapt
 410 | test scope to the model's specific features (e.g., add MoE-specific tests only if the
 411 | model has MoE).
 412 | 
 413 | ## Reference Implementations
 414 | 
 415 | | Model | Directory                                 | Features                                                |
 416 | | ----- | ----------------------------------------- | ------------------------------------------------------- |
 417 | | Qwen2 | `areal/experimental/models/archon/qwen2/` | Dense, attention bias, no QK norm                       |
 418 | | Qwen3 | `areal/experimental/models/archon/qwen3/` | Dense + MoE, QK norm, no attention bias, shared experts |
 419 | 
 420 | ## Architecture Decision Map
 421 | 
 422 | | Feature             | qwen2    | qwen3                      | What to check in target model                            |
 423 | | ------------------- | -------- | -------------------------- | -------------------------------------------------------- |
 424 | | Attention bias      | Yes      | No                         | `attention_bias` in HF config                            |
 425 | | QK norm             | No       | Yes                        | `qk_norm` in HF config or QKNorm module in modeling file |
 426 | | MoE                 | No       | Yes                        | `num_experts`/`num_local_experts` in HF config           |
 427 | | Shared experts      | No       | Yes                        | `num_shared_experts` in HF config                        |
 428 | | Decoder sparse step | No       | Yes                        | `decoder_sparse_step` in HF config                       |
 429 | | Weight tying        | Both     | Both                       | `tie_word_embeddings` in HF config                       |
 430 | | RoPE                | Standard | Standard (re-export qwen2) | Check inv_freq formula in HF modeling code               |
 431 | 
 432 | ## Common Mistakes
 433 | 
 434 | - Not mapping all HF keys in `state_dict_adapter.py` (causes silent weight drops)
 435 | - Wrong `from_hf_config()` field mapping (uses wrong HF config attribute name)
 436 | - Forgetting to handle `None` keys in `from_hf_map` (keys to skip like
 437 |   `rotary_emb.inv_freq`)
 438 | - Missing MoE expert weight 3D\<->2D conversion when model has MoE
 439 | - Wrong TP plan for attention with/without QK norm (`use_local_output` must match)
 440 | - Forgetting to add import line in `areal/experimental/models/archon/__init__.py`
 441 | - Not including all `model_type` variants in `supported_model_types` frozenset
 442 | - Using `print` instead of `areal.utils.logging.getLogger()`
 443 | 
 444 | ## File Checklist
 445 | 
 446 | After completion, verify all files exist and are consistent:
 447 | 
 448 | - [ ] `areal/experimental/models/archon/<model>/__init__.py`
 449 | - [ ] `areal/experimental/models/archon/<model>/spec.py` -- ModelSpec + register
 450 | - [ ] `areal/experimental/models/archon/<model>/model/args.py` -- ModelArgs +
 451 |   from_hf_config
 452 | - [ ] `areal/experimental/models/archon/<model>/model/model.py` -- Model + Attention +
 453 |   FFN
 454 | - [ ] `areal/experimental/models/archon/<model>/model/rope.py` -- RoPE (or re-export)
 455 | - [ ] `areal/experimental/models/archon/<model>/model/state_dict_adapter.py` -- Key
 456 |   mapping
 457 | - [ ] `areal/experimental/models/archon/<model>/infra/parallelize.py` -- Parallel
 458 |   strategy
 459 | - [ ] `areal/experimental/models/archon/__init__.py` -- Import line added
 460 | - [ ] `tests/experimental/archon/test_<model>_*.py` -- Tests
 461 | 
 462 | ______________________________________________________________________
 463 | 
 464 | <!--
 465 | ================================================================================
 466 |                             MAINTAINER GUIDE
 467 | ================================================================================
 468 | 
 469 | Canonical location: .agents/skills/add-archon-model/SKILL.md
 470 | Mirrors: .opencode/skills/add-archon-model/SKILL.md, .claude/skills/add-archon-model/SKILL.md
 471 | Invocation: $add-archon-model (Codex) / /add-archon-model (OpenCode, Claude Code)
 472 | 
 473 | ## Purpose
 474 | 
 475 | Semi-automated guide for adding new model architectures to the Archon training engine.
 476 | Unlike simpler skills (add-reward, add-dataset), this skill actively guides the agent to:
 477 | 1. Analyze HuggingFace source code to extract architecture details
 478 | 2. Select the closest reference implementation (qwen2 or qwen3)
 479 | 3. Generate code skeletons adapted to the target architecture
 480 | 4. Create appropriate tests based on existing test patterns
 481 | 
 482 | ## How to Update
 483 | 
 484 | ### When New Reference Models Are Added
 485 | 1. Add to "Reference Implementations" table
 486 | 2. Update "Architecture Decision Map" with new feature columns
 487 | 3. Update Step 2 (reference selection) with new options
 488 | 
 489 | ### When Base Classes Change
 490 | 1. Update contract signatures in Steps 3, 4, 6, 7
 491 | 2. Update file checklist if new files are required
 492 | 
 493 | ### When ModelSpec Changes
 494 | 1. Update Step 8 with new ModelSpec fields
 495 | 2. Update spec.py template
 496 | 
 497 | ### When Test Patterns Change
 498 | 1. Update Step 10 with new test patterns
 499 | 2. Do NOT hardcode test categories -- keep it flexible
 500 | 
 501 | ### Important Design Decisions
 502 | - This skill is SEMI-AUTOMATED: Claude should read HF source and generate code,
 503 |   not just provide templates for the user to fill in manually
 504 | - The skill references existing test files rather than hardcoding test categories,
 505 |   ensuring it stays current as the test suite evolves
 506 | - Reference model selection (qwen2 vs qwen3) is based on MoE and QK norm presence
 507 | 
 508 | ================================================================================
 509 | -->
```


---
## .agents/skills/add-dataset/SKILL.md

```
   1 | ---
   2 | name: add-dataset
   3 | description: Guide for adding a new dataset loader to AReaL. Use when user wants to add a new dataset.
   4 | ---
   5 | 
   6 | # Add Dataset
   7 | 
   8 | Add a new dataset loader to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a dataset?"
  15 | - User wants to integrate a new dataset
  16 | - User mentions creating a dataset loader
  17 | 
  18 | ## Step-by-Step Guide
  19 | 
  20 | ### Step 1: Create Dataset File
  21 | 
  22 | Create `areal/dataset/<name>.py`:
  23 | 
  24 | ```python
  25 | from datasets import Dataset, load_dataset
  26 | 
  27 | 
  28 | def get_<name>_sft_dataset(
  29 |     path: str,
  30 |     split: str,
  31 |     tokenizer,
  32 |     max_length: int | None = None,
  33 | ) -> Dataset:
  34 |     """Load dataset for SFT training.
  35 | 
  36 |     Args:
  37 |         path: Path to dataset (HuggingFace hub or local path)
  38 |         split: Dataset split (train/validation/test)
  39 |         tokenizer: Tokenizer for processing
  40 |         max_length: Maximum sequence length (optional)
  41 | 
  42 |     Returns:
  43 |         HuggingFace Dataset with processed samples
  44 |     """
  45 |     dataset = load_dataset(path=path, split=split)
  46 | 
  47 |     def process(sample):
  48 |         # Tokenize the full sequence (prompt + response)
  49 |         seq_token = tokenizer.encode(
  50 |             sample["question"] + sample["answer"] + tokenizer.eos_token
  51 |         )
  52 |         prompt_token = tokenizer.encode(sample["question"])
  53 |         # Loss mask: 0 for prompt, 1 for response
  54 |         loss_mask = [0] * len(prompt_token) + [1] * (len(seq_token) - len(prompt_token))
  55 |         return {"input_ids": seq_token, "loss_mask": loss_mask}
  56 | 
  57 |     dataset = dataset.map(process).remove_columns(["question", "answer"])
  58 | 
  59 |     if max_length is not None:
  60 |         dataset = dataset.filter(lambda x: len(x["input_ids"]) <= max_length)
  61 | 
  62 |     return dataset
  63 | 
  64 | 
  65 | def get_<name>_rl_dataset(
  66 |     path: str,
  67 |     split: str,
  68 |     tokenizer,
  69 |     max_length: int | None = None,
  70 | ) -> Dataset:
  71 |     """Load dataset for RL training.
  72 | 
  73 |     Args:
  74 |         path: Path to dataset
  75 |         split: Dataset split
  76 |         tokenizer: Tokenizer for length filtering
  77 |         max_length: Maximum sequence length
  78 | 
  79 |     Returns:
  80 |         HuggingFace Dataset with prompts and answers for reward computation
  81 |     """
  82 |     dataset = load_dataset(path=path, split=split)
  83 | 
  84 |     def process(sample):
  85 |         messages = [
  86 |             {
  87 |                 "role": "user",
  88 |                 "content": sample["question"],
  89 |             }
  90 |         ]
  91 |         return {"messages": messages, "answer": sample["answer"]}
  92 | 
  93 |     dataset = dataset.map(process).remove_columns(["question"])
  94 | 
  95 |     if max_length is not None:
  96 | 
  97 |         def filter_length(sample):
  98 |             content = sample["messages"][0]["content"]
  99 |             tokens = tokenizer.encode(content)
 100 |             return len(tokens) <= max_length
 101 | 
 102 |         dataset = dataset.filter(filter_length)
 103 | 
 104 |     return dataset
 105 | ```
 106 | 
 107 | ### Step 2: Register in __init__.py
 108 | 
 109 | Update `areal/dataset/__init__.py`:
 110 | 
 111 | ```python
 112 | # Add to VALID_DATASETS
 113 | VALID_DATASETS = [
 114 |     # ... existing datasets
 115 |     "<name>",
 116 | ]
 117 | 
 118 | # Add to _get_custom_dataset function
 119 | def _get_custom_dataset(name: str, ...):
 120 |     # ... existing code
 121 |     elif name == "<name>":
 122 |         from areal.dataset.<name> import get_<name>_sft_dataset, get_<name>_rl_dataset
 123 |         if dataset_type == "sft":
 124 |             return get_<name>_sft_dataset(path, split, max_length, tokenizer)
 125 |         else:
 126 |             return get_<name>_rl_dataset(path, split, max_length, tokenizer)
 127 | ```
 128 | 
 129 | ### Step 3: Add Config (Optional)
 130 | 
 131 | If the dataset needs special configuration, add to `areal/api/cli_args.py`:
 132 | 
 133 | ```python
 134 | @dataclass
 135 | class TrainDatasetConfig:
 136 |     # ... existing fields
 137 |     <name>_specific_field: Optional[str] = None
 138 | ```
 139 | 
 140 | ### Step 4: Add Tests
 141 | 
 142 | Create `tests/test_<name>_dataset.py`:
 143 | 
 144 | ```python
 145 | import pytest
 146 | from areal.dataset.<name> import get_<name>_sft_dataset, get_<name>_rl_dataset
 147 | 
 148 | def test_sft_dataset_loads(tokenizer):
 149 |     dataset = get_<name>_sft_dataset("path/to/data", split="train", tokenizer=tokenizer)
 150 |     assert len(dataset) > 0
 151 |     assert "input_ids" in dataset.column_names
 152 |     assert "loss_mask" in dataset.column_names
 153 | 
 154 | def test_rl_dataset_loads(tokenizer):
 155 |     dataset = get_<name>_rl_dataset("path/to/data", split="train", tokenizer=tokenizer)
 156 |     assert len(dataset) > 0
 157 |     assert "messages" in dataset.column_names
 158 |     assert "answer" in dataset.column_names
 159 | ```
 160 | 
 161 | ## Reference Implementations
 162 | 
 163 | | Dataset    | File                               | Description              |
 164 | | ---------- | ---------------------------------- | ------------------------ |
 165 | | GSM8K      | `areal/dataset/gsm8k.py`           | Math word problems       |
 166 | | Geometry3K | `areal/dataset/geometry3k.py`      | Geometry problems        |
 167 | | CLEVR      | `areal/dataset/clevr_count_70k.py` | Visual counting          |
 168 | | HH-RLHF    | `areal/dataset/hhrlhf.py`          | Helpfulness/Harmlessness |
 169 | | TORL       | `areal/dataset/torl_data.py`       | Tool-use RL              |
 170 | 
 171 | ## Required Fields
 172 | 
 173 | ### SFT Dataset
 174 | 
 175 | ```python
 176 | {
 177 |     "messages": [
 178 |         {"role": "user", "content": "..."},
 179 |         {"role": "assistant", "content": "..."},
 180 |     ]
 181 | }
 182 | ```
 183 | 
 184 | ### RL Dataset
 185 | 
 186 | ```python
 187 | {
 188 |     "messages": [
 189 |         {"role": "user", "content": "..."},
 190 |     ],
 191 |     "answer": "ground_truth_for_reward",
 192 |     # Optional metadata for reward function
 193 | }
 194 | ```
 195 | 
 196 | ## Common Mistakes
 197 | 
 198 | - Returning `List[Dict]` instead of HuggingFace `Dataset`
 199 | - Using Python loops instead of `dataset.map()`/`filter()`
 200 | - Missing `"messages"` field for RL datasets
 201 | - Wrong message format (should be list of dicts with `role` and `content`)
 202 | - Not registering in `__init__.py`
```


---
## .agents/skills/add-reward/SKILL.md

```
   1 | ---
   2 | name: add-reward
   3 | description: Guide for adding a new reward function to AReaL. Use when user wants to create a reward function.
   4 | ---
   5 | 
   6 | # Add Reward
   7 | 
   8 | Add a new reward function to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a reward function?"
  15 | - User wants to implement custom rewards
  16 | - User mentions reward computation
  17 | 
  18 | ## Step-by-Step Guide
  19 | 
  20 | ### Step 1: Create Reward File
  21 | 
  22 | Create `areal/reward/<name>.py`:
  23 | 
  24 | ```python
  25 | from typing import Any
  26 | 
  27 | from areal.utils import logging
  28 | 
  29 | logger = logging.getLogger("MyReward")
  30 | 
  31 | 
  32 | def <name>_reward_fn(
  33 |     prompt: str,
  34 |     completions: str,
  35 |     prompt_ids,
  36 |     completion_ids,
  37 |     answer: str | None = None,
  38 |     **kwargs: Any,
  39 | ) -> float:
  40 |     """Compute reward for a single completion.
  41 | 
  42 |     Args:
  43 |         prompt: Prompt string
  44 |         completions: Completion string (model output)
  45 |         prompt_ids: Tokenized prompt IDs
  46 |         completion_ids: Tokenized completion IDs
  47 |         answer: Ground truth answer from dataset (optional)
  48 |         **kwargs: Additional data from dataset
  49 | 
  50 |     Returns:
  51 |         Reward value (float), typically 0.0 or 1.0
  52 |     """
  53 |     try:
  54 |         # Extract answer from completion
  55 |         extracted = _extract_answer(completions)
  56 | 
  57 |         # Compare with ground truth
  58 |         if answer is not None and extracted == str(answer):
  59 |             return 1.0
  60 |         return 0.0
  61 |     except Exception:
  62 |         logger.warning("Exception in reward computation", exc_info=True)
  63 |         return 0.0
  64 | 
  65 | 
  66 | def _extract_answer(completion: str) -> str:
  67 |     """Extract the answer from a completion string.
  68 | 
  69 |     Implement your extraction logic here.
  70 |     """
  71 |     # Example: Extract content from \boxed{}
  72 |     import re
  73 | 
  74 |     match = re.search(r"\\boxed\{([^}]+)\}", completion)
  75 |     if match:
  76 |         return match.group(1).strip()
  77 |     return completion.strip()
  78 | ```
  79 | 
  80 | ### Step 2: Register in __init__.py
  81 | 
  82 | Update `areal/reward/__init__.py`:
  83 | 
  84 | ```python
  85 | # Add to VALID_REWARD_FN
  86 | VALID_REWARD_FN = [
  87 |     # ... existing reward functions
  88 |     "<name>",
  89 | ]
  90 | 
  91 | # Add to get_reward_fn function
  92 | def get_reward_fn(name: str, **kwargs):
  93 |     # ... existing code
  94 |     elif name == "<name>":
  95 |         from areal.reward.<name> import <name>_reward_fn
  96 |         return <name>_reward_fn
  97 | ```
  98 | 
  99 | ### Step 3: Handle Blocking Operations
 100 | 
 101 | If your reward function uses blocking operations (e.g., API calls, model inference), the
 102 | workflow will wrap it with `AsyncRewardWrapper`:
 103 | 
 104 | ```python
 105 | # In your workflow
 106 | from areal.reward import AsyncRewardWrapper
 107 | 
 108 | self.reward_fn = AsyncRewardWrapper(reward_fn)
 109 | 
 110 | # Then call it asynchronously
 111 | rewards = await self.reward_fn(prompt, completions, **data)
 112 | ```
 113 | 
 114 | ### Step 4: Add Tests
 115 | 
 116 | Create `tests/test_<name>_reward.py`:
 117 | 
 118 | ```python
 119 | import pytest
 120 | from areal.reward.<name> import <name>_reward_fn
 121 | 
 122 | def test_reward_correct_answer():
 123 |     reward = <name>_reward_fn(
 124 |         prompt="What is 2+2?",
 125 |         completions="The answer is \\boxed{4}",
 126 |         prompt_ids=None,
 127 |         completion_ids=None,
 128 |         answer="4",
 129 |     )
 130 |     assert reward == 1.0
 131 | 
 132 | def test_reward_wrong_answer():
 133 |     reward = <name>_reward_fn(
 134 |         prompt="What is 2+2?",
 135 |         completions="The answer is \\boxed{5}",
 136 |         prompt_ids=None,
 137 |         completion_ids=None,
 138 |         answer="4",
 139 |     )
 140 |     assert reward == 0.0
 141 | ```
 142 | 
 143 | ## Reference Implementations
 144 | 
 145 | | Reward     | File                              | Description                  |
 146 | | ---------- | --------------------------------- | ---------------------------- |
 147 | | GSM8K      | `areal/reward/gsm8k.py`           | Math answer verification     |
 148 | | Geometry3K | `areal/reward/geometry3k.py`      | Geometry answer verification |
 149 | | CLEVR      | `areal/reward/clevr_count_70k.py` | Counting verification        |
 150 | | MathVerify | `areal/reward/math_verify.py`     | General math verification    |
 151 | 
 152 | ## Function Signature
 153 | 
 154 | All reward functions must follow this signature:
 155 | 
 156 | ```python
 157 | def reward_fn(
 158 |     prompt: str,               # Input prompt string
 159 |     completions: str,          # Model completion string
 160 |     prompt_ids,                # Tokenized prompt
 161 |     completion_ids,            # Tokenized completion
 162 |     **kwargs: Any,             # Additional data from dataset (e.g., answer)
 163 | ) -> float:                    # Reward value (typically 0.0 or 1.0)
 164 | ```
 165 | 
 166 | **Note**: The reward function is called once per sample. Batching is handled by
 167 | `AsyncRewardWrapper` in the workflow.
 168 | 
 169 | ## Key Requirements
 170 | 
 171 | 1. **Deterministic**: Same inputs should produce same outputs
 172 | 1. **Return float**: Output is a single float value per sample
 173 | 1. **No blocking in async context**: Use `AsyncRewardWrapper` if needed
 174 | 1. **Logging**: Use `areal.utils.logging`, not `print`
 175 | 1. **Handle exceptions**: Return 0.0 on error, don't raise
 176 | 
 177 | ## Common Mistakes
 178 | 
 179 | - Returning a tensor instead of a float
 180 | - Expecting batched inputs (reward is called per sample)
 181 | - Non-deterministic behavior
 182 | - Blocking operations without `AsyncRewardWrapper`
 183 | - Raising exceptions instead of returning 0.0
```


---
## .agents/skills/add-unit-tests/SKILL.md

```
   1 | ---
   2 | name: add-unit-tests
   3 | description: Guide for adding unit tests to AReaL. Use when user wants to add tests for new functionality or increase test coverage.
   4 | ---
   5 | 
   6 | # Add Unit Tests
   7 | 
   8 | Add unit tests to AReaL following the project's testing conventions.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add tests?"
  15 | - User wants to increase test coverage
  16 | - User needs to write tests for new functionality
  17 | - User wants to understand AReaL testing patterns
  18 | 
  19 | ## Step-by-Step Guide
  20 | 
  21 | ### Step 1: Understand Test Types
  22 | 
  23 | AReaL has two main test categories:
  24 | 
  25 | | Test Type             | Purpose                            | Location Pattern                   | How It Runs                                |
  26 | | --------------------- | ---------------------------------- | ---------------------------------- | ------------------------------------------ |
  27 | | **Unit Tests**        | Test individual functions/modules  | `tests/test_<module>_<feature>.py` | Directly via pytest                        |
  28 | | **Distributed Tests** | Test distributed/parallel behavior | `tests/torchrun/run_*.py`          | Via torchrun (called by pytest subprocess) |
  29 | 
  30 | **Note**: All tests are invoked via pytest. Distributed tests use `torchrun` but are
  31 | still called from pytest test files.
  32 | 
  33 | ### Step 2: Create Test File Structure
  34 | 
  35 | Create test file with naming convention: `test_<module>_<feature>.py`
  36 | 
  37 | ```python
  38 | import pytest
  39 | import torch
  40 | 
  41 | # Import the module to test
  42 | from areal.dataset.gsm8k import get_gsm8k_sft_dataset
  43 | from tests.utils import get_dataset_path  # Optional test utilities
  44 | # For mocking tokenizer: from unittest.mock import MagicMock
  45 | ```
  46 | 
  47 | ### Step 3: Write Test Functions
  48 | 
  49 | Follow Arrange-Act-Assert pattern:
  50 | 
  51 | ```python
  52 | def test_function_under_condition_returns_expected():
  53 |     """Test that function returns expected value under condition."""
  54 |     # Arrange
  55 |     input_data = 5
  56 |     expected_output = 10
  57 | 
  58 |     # Act
  59 |     result = function_under_test(input_data)
  60 | 
  61 |     # Assert
  62 |     assert result == expected_output
  63 | ```
  64 | 
  65 | ### Step 4: Add Pytest Markers and CI Strategy
  66 | 
  67 | Use appropriate pytest markers:
  68 | 
  69 | | Marker                                  | When to Use                                                  |
  70 | | --------------------------------------- | ------------------------------------------------------------ |
  71 | | `@pytest.mark.slow`                     | Test takes > 10 seconds (excluded from CI by default)        |
  72 | | `@pytest.mark.ci`                       | Slow test that must run in CI (use with `@pytest.mark.slow`) |
  73 | | `@pytest.mark.asyncio`                  | Async test functions                                         |
  74 | | `@pytest.mark.skipif(cond, reason=...)` | Conditional skip                                             |
  75 | | `@pytest.mark.parametrize(...)`         | Parameterized tests                                          |
  76 | 
  77 | **CI Test Strategy**:
  78 | 
  79 | - `@pytest.mark.slow`: Excluded from CI by default (CI runs `pytest -m "not slow"`)
  80 | - `@pytest.mark.slow` + `@pytest.mark.ci`: Slow but must run in CI
  81 | - No marker: Runs in CI (fast unit tests)
  82 | 
  83 | ```python
  84 | @pytest.mark.asyncio
  85 | async def test_async_function():
  86 |     result = await async_function()
  87 |     assert result == expected
  88 | 
  89 | @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
  90 | def test_gpu_feature():
  91 |     tensor = torch.tensor([1, 2, 3], device="cuda")
  92 |     # ... assertions
  93 | 
  94 | @pytest.mark.parametrize("batch_size", [1, 4, 16])
  95 | def test_with_parameters(batch_size):
  96 |     # Parameterized test
  97 | 
  98 | @pytest.mark.slow
  99 | def test_slow_function():
 100 |     # Excluded from CI by default
 101 | 
 102 | @pytest.mark.slow
 103 | @pytest.mark.ci
 104 | def test_slow_but_required_in_ci():
 105 |     # Slow but must run in CI
 106 | ```
 107 | 
 108 | ### Step 5: Mock Distributed Environment
 109 | 
 110 | For unit tests that need distributed mocks:
 111 | 
 112 | ```python
 113 | import torch.distributed as dist
 114 | 
 115 | def test_distributed_function(monkeypatch):
 116 |     monkeypatch.setattr(dist, "get_rank", lambda: 0)
 117 |     monkeypatch.setattr(dist, "get_world_size", lambda: 2)
 118 |     result = distributed_function()
 119 |     assert result == expected
 120 | ```
 121 | 
 122 | ### Step 6: Handle GPU Dependencies
 123 | 
 124 | Always skip gracefully when GPU unavailable:
 125 | 
 126 | ```python
 127 | CUDA_AVAILABLE = torch.cuda.is_available()
 128 | 
 129 | @pytest.mark.skipif(not CUDA_AVAILABLE, reason="CUDA not available")
 130 | def test_gpu_function():
 131 |     tensor = torch.tensor([1, 2, 3], device="cuda")
 132 |     # ... assertions
 133 | ```
 134 | 
 135 | ## Key Requirements (Based on testing.md)
 136 | 
 137 | ### Mocking Distributed
 138 | 
 139 | - Use `torch.distributed.fake_pg` for unit tests
 140 | - Mock `dist.get_rank()` and `dist.get_world_size()` explicitly
 141 | - Don't mock internals of FSDP/DTensor
 142 | 
 143 | ### GPU Test Constraints
 144 | 
 145 | - **Always skip gracefully** when GPU unavailable
 146 | - Clean up GPU memory: `torch.cuda.empty_cache()` in fixtures
 147 | - Use smallest possible model/batch for unit tests
 148 | 
 149 | ### Assertions
 150 | 
 151 | - Use `torch.testing.assert_close()` for tensor comparison
 152 | - Specify `rtol`/`atol` explicitly for numerical tests
 153 | - Avoid bare `assert tensor.equal()` - no useful error message
 154 | 
 155 | ## Reference Implementations
 156 | 
 157 | | Test File                        | Description                            | Key Patterns                                      |
 158 | | -------------------------------- | -------------------------------------- | ------------------------------------------------- |
 159 | | `tests/test_utils.py`            | Utility function tests                 | Fixtures, parametrized tests                      |
 160 | | `tests/test_examples.py`         | Integration tests with dataset loading | Dataset path resolution, success pattern matching |
 161 | | `tests/test_fsdp_engine_nccl.py` | Distributed tests                      | Torchrun integration                              |
 162 | 
 163 | ## Common Mistakes
 164 | 
 165 | - **Missing test file registration**: Ensure file follows `test_*.py` naming
 166 | - **GPU dependency without skip**: Always use `@pytest.mark.skipif` for GPU tests
 167 | - **Incorrect tensor comparisons**: Use `torch.testing.assert_close()` not
 168 |   `assert tensor.equal()`
 169 | - **Memory leaks in GPU tests**: Clean up with `torch.cuda.empty_cache()`
 170 | - **Mocking too much**: Don't mock FSDP/DTensor internals
 171 | - **Unclear test names**: Follow `test_<what>_<condition>_<expected>` pattern
 172 | - **No docstrings**: Add descriptive docstrings to test functions
 173 | 
 174 | ## Integration with Other Skills
 175 | 
 176 | This skill complements other AReaL development skills:
 177 | 
 178 | - **After `/add-dataset`**: Add tests for new dataset loaders
 179 | - **After `/add-workflow`**: Add tests for new workflows
 180 | - **After `/add-reward`**: Add tests for new reward functions
 181 | - **With expert agents**: Reference this skill when planning test implementation
 182 | 
 183 | ## Running Tests
 184 | 
 185 | ```bash
 186 | # First check GPU availability (many tests require GPU)
 187 | python -c "import torch; print('GPU available:', torch.cuda.is_available())"
 188 | 
 189 | # Run specific test file
 190 | uv run pytest tests/test_<name>.py
 191 | 
 192 | # Skip slow tests (CI default)
 193 | uv run pytest -m "not slow"
 194 | 
 195 | # Run with verbose output
 196 | uv run pytest -v
 197 | 
 198 | # Run distributed tests (requires torchrun and multi-GPU)
 199 | # Note: Usually invoked via pytest test files
 200 | torchrun --nproc_per_node=2 tests/torchrun/run_<test>.py
 201 | ```
```


---
## .agents/skills/add-workflow/SKILL.md

```
   1 | ---
   2 | name: add-workflow
   3 | description: Guide for adding a new RolloutWorkflow to AReaL. Use when user wants to create a new workflow.
   4 | ---
   5 | 
   6 | # Add Workflow
   7 | 
   8 | Add a new RolloutWorkflow implementation to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a workflow?"
  15 | - User wants to create a new RolloutWorkflow
  16 | - User mentions implementing a custom rollout
  17 | 
  18 | ## Prerequisites
  19 | 
  20 | Before starting, ensure you understand:
  21 | 
  22 | - The workflow's purpose and requirements
  23 | - Input/output data format
  24 | - Reward function to use
  25 | 
  26 | ## Step-by-Step Guide
  27 | 
  28 | ### Step 1: Create Workflow File
  29 | 
  30 | Create `areal/workflow/<name>.py`:
  31 | 
  32 | ```python
  33 | import uuid
  34 | from typing import Any, Callable
  35 | 
  36 | import torch
  37 | 
  38 | from areal.api.cli_args import GenerationHyperparameters
  39 | from areal.api.engine_api import InferenceEngine
  40 | from areal.api.io_struct import ModelRequest, ModelResponse
  41 | from areal.api.reward_api import AsyncRewardWrapper
  42 | from areal.api.workflow_api import RolloutWorkflow
  43 | from areal.utils import logging
  44 | 
  45 | logger = logging.getLogger("MyWorkflow")
  46 | 
  47 | 
  48 | class MyWorkflow(RolloutWorkflow):
  49 |     """Description of your workflow."""
  50 | 
  51 |     def __init__(
  52 |         self,
  53 |         gconfig: GenerationHyperparameters,
  54 |         tokenizer,
  55 |         reward_fn: Callable,
  56 |     ):
  57 |         self.gconfig = gconfig.new_with_stop_and_pad_token_ids(tokenizer)
  58 |         self.tokenizer = tokenizer
  59 |         self.async_reward_fn = AsyncRewardWrapper(reward_fn)
  60 | 
  61 |     async def arun_episode(
  62 |         self,
  63 |         engine: InferenceEngine,
  64 |         data: dict[str, Any],
  65 |     ) -> dict[str, Any] | None | dict[str, InteractionWithTokenLogpReward]:
  66 |         """Run a single episode. MUST be async and non-blocking."""
  67 | 
  68 |         # 1. Prepare input_ids from data
  69 |         input_ids = self.tokenizer.apply_chat_template(
  70 |             data["messages"],
  71 |             tokenize=True,
  72 |             add_generation_prompt=True,
  73 |         )
  74 | 
  75 |         # 2. Build ModelRequest
  76 |         req = ModelRequest(
  77 |             rid=uuid.uuid4().hex,
  78 |             input_ids=list(input_ids),
  79 |             gconfig=self.gconfig.new(n_samples=1),
  80 |             tokenizer=self.tokenizer,
  81 |         )
  82 | 
  83 |         # 3. Generate completion (async)
  84 |         resp: ModelResponse = await engine.agenerate(req)
  85 | 
  86 |         # 4. Compute reward (async)
  87 |         prompt_str = self.tokenizer.decode(input_ids)
  88 |         completion_str = self.tokenizer.decode(resp.output_tokens)
  89 |         reward = await self.async_reward_fn(
  90 |             prompt_str,
  91 |             completion_str,
  92 |             resp.input_tokens,
  93 |             resp.output_tokens,
  94 |             **data,
  95 |         )
  96 | 
  97 |         # 5. Return results in expected format
  98 |         return {
  99 |             "input_ids": torch.tensor(resp.input_tokens),
 100 |             "output_ids": torch.tensor(resp.output_tokens),
 101 |             "reward": torch.tensor(reward),
 102 |         }
 103 | ```
 104 | 
 105 | ### Step 2: Register in __init__.py
 106 | 
 107 | Add to `areal/workflow/__init__.py`:
 108 | 
 109 | ```python
 110 | from areal.workflow.<name> import MyWorkflow
 111 | 
 112 | __all__ = [
 113 |     # ... existing exports
 114 |     "MyWorkflow",
 115 | ]
 116 | ```
 117 | 
 118 | ### Step 3: Update Entry Script
 119 | 
 120 | Update your training script to use the new workflow:
 121 | 
 122 | ```python
 123 | trainer.train(
 124 |     workflow="areal.workflow.<name>.MyWorkflow",
 125 |     # ... other args
 126 | )
 127 | ```
 128 | 
 129 | ### Step 4: Add Tests
 130 | 
 131 | Create `tests/test_<name>_workflow.py`:
 132 | 
 133 | ```python
 134 | import pytest
 135 | from areal.workflow.<name> import MyWorkflow
 136 | 
 137 | @pytest.mark.asyncio
 138 | async def test_workflow_basic():
 139 |     # Test basic functionality
 140 |     pass
 141 | ```
 142 | 
 143 | ## Reference Implementations
 144 | 
 145 | | Workflow           | File                            | Description                |
 146 | | ------------------ | ------------------------------- | -------------------------- |
 147 | | MultiTurnWorkflow  | `areal/workflow/multi_turn.py`  | Multi-turn conversation    |
 148 | | RLVRWorkflow       | `areal/workflow/rlvr.py`        | RL with verifiable rewards |
 149 | | VisionRLVRWorkflow | `areal/workflow/vision_rlvr.py` | Vision + RLVR              |
 150 | 
 151 | ## Key Requirements
 152 | 
 153 | 1. **Async**: `arun_episode` must be `async def` and non-blocking
 154 | 1. **No sync I/O**: Use `aiofiles` for file operations
 155 | 1. **Wrap rewards**: Use `AsyncRewardWrapper` for reward functions
 156 | 1. **Tensor format**: Output tensors should be `[batch, seq_len, ...]`
 157 | 1. **Use helpers**: `concat_padded_tensors` for combining outputs
 158 | 
 159 | ## Common Mistakes
 160 | 
 161 | - Using `open()` instead of `aiofiles.open()`
 162 | - Forgetting to `await` async calls
 163 | - Not wrapping reward function with `AsyncRewardWrapper`
 164 | - Wrong tensor shape conventions
```


---
## .agents/skills/commit-conventions/SKILL.md

```
   1 | ---
   2 | name: commit-conventions
   3 | description: AReaL commit message conventions. MUST load on every git commit -- provides Conventional Commits format with scope inference from file paths.
   4 | ---
   5 | 
   6 | # Commit Conventions
   7 | 
   8 | Commit message conventions and scope inference rules for the AReaL repository.
   9 | 
  10 | ## When to Use
  11 | 
  12 | **ALWAYS load this skill when making any git commit in AReaL.** This includes:
  13 | 
  14 | - Direct commits (`git commit`)
  15 | - Commits during PR creation (`$create-pr` / `/create-pr`)
  16 | - Commits delegated to sub-agents with this skill loaded
  17 | - Any agent workflow that produces a commit
  18 | 
  19 | ## Commit Message Format
  20 | 
  21 | ```
  22 | <type>(<scope>): <subject>
  23 | 
  24 | <body>
  25 | 
  26 | [Optional sections:]
  27 | Key changes:
  28 | - change 1
  29 | - change 2
  30 | 
  31 | Refs: #123, #456
  32 | ```
  33 | 
  34 | ## Type Selection
  35 | 
  36 | | Type       | When to Use                     |
  37 | | ---------- | ------------------------------- |
  38 | | `feat`     | New feature or capability       |
  39 | | `fix`      | Bug fix                         |
  40 | | `docs`     | Documentation only              |
  41 | | `refactor` | Code change without feature/fix |
  42 | | `test`     | Adding or fixing tests          |
  43 | | `chore`    | Build, deps, config changes     |
  44 | | `perf`     | Performance improvement         |
  45 | 
  46 | ## Scope Inference
  47 | 
  48 | Infer scope from the **primary** changed file paths:
  49 | 
  50 | | File Path Pattern                                            | Scope                          |
  51 | | ------------------------------------------------------------ | ------------------------------ |
  52 | | `areal/workflow/`                                            | `workflow`                     |
  53 | | `areal/engine/`                                              | `engine`                       |
  54 | | `areal/reward/`                                              | `reward`                       |
  55 | | `areal/dataset/`                                             | `dataset`                      |
  56 | | `areal/api/`                                                 | `api`                          |
  57 | | `areal/utils/`                                               | `utils`                        |
  58 | | `areal/infra/`                                               | `infra`                        |
  59 | | `areal/trainer/`                                             | `trainer`                      |
  60 | | `areal/models/`                                              | `models`                       |
  61 | | `areal/experimental/`                                        | `archon`                       |
  62 | | `docs/`                                                      | `docs`                         |
  63 | | `examples/`                                                  | `examples`                     |
  64 | | `AGENTS.md`, `.agents/`, `.claude/`, `.codex/`, `.opencode/` | `agents`                       |
  65 | | Multiple areas                                               | Omit scope or use broader term |
  66 | 
  67 | ## Rules
  68 | 
  69 | - **Subject**: imperative mood, ~50-72 chars, no trailing period
  70 | - **Body**: explain "why" not "what", wrap at 72 chars
  71 | - **Key changes**: bullet list of main modifications (for complex commits with 3+ files)
  72 | - **Refs**: reference issues/PRs if applicable
  73 | 
  74 | ## Examples
  75 | 
  76 | **Single file fix:**
  77 | 
  78 | ```
  79 | fix(reward): handle empty completion in gsm8k
  80 | 
  81 | Return 0 reward instead of raising exception when
  82 | completion string is empty after extraction.
  83 | ```
  84 | 
  85 | **Multi-file feature:**
  86 | 
  87 | ```
  88 | feat(engine): add CPU offload support to ArchonEngine
  89 | 
  90 | Enable torch_memory_saver for model offloading during
  91 | rollout phase to reduce GPU memory pressure.
  92 | 
  93 | Key changes:
  94 | - Add offload/onload methods to ArchonEngine
  95 | - Integrate with weight update flow
  96 | - Handle ROCm compatibility
  97 | ```
  98 | 
  99 | **Docs only:**
 100 | 
 101 | ```
 102 | docs: update algorithm comparison table
 103 | 
 104 | Add SAPO and GSPO to the algorithm family documentation
 105 | with configuration examples.
 106 | ```
 107 | 
 108 | **Agent/tooling changes:**
 109 | 
 110 | ```
 111 | chore(agents): port review-pr command to OpenCode
 112 | 
 113 | Add OpenCode-native commands with task() category
 114 | delegation instead of hardcoded model names.
 115 | 
 116 | Key changes:
 117 | - Create .opencode/command/ with review-pr, create-pr
 118 | - Replace Opus/Sonnet/Haiku with deep/unspecified-high/quick
 119 | - Add expert subagent consultation patterns
 120 | ```
 121 | 
 122 | ______________________________________________________________________
 123 | 
 124 | <!--
 125 | ================================================================================
 126 |                             MAINTAINER GUIDE
 127 | ================================================================================
 128 | 
 129 | Canonical location: .agents/skills/commit-conventions/SKILL.md
 130 | Mirrors: .opencode/skills/commit-conventions/SKILL.md, .claude/skills/commit-conventions/SKILL.md
 131 | Invocation: Automatically loaded on every git commit (all platforms)
 132 | 
 133 | ## Purpose
 134 | 
 135 | Provides Conventional Commits format with AReaL-specific scope inference
 136 | from file paths. Unlike other skills, this one is NOT user-triggered --
 137 | it is loaded by the system/agent on every commit operation.
 138 | 
 139 | ## How to Update
 140 | 
 141 | ### When New Modules Are Added
 142 | 1. Add the file path pattern and scope to the "Scope Inference" table
 143 | 2. Keep table sorted by areal/ subpackages first, then top-level dirs
 144 | 
 145 | ### When Commit Types Change
 146 | 1. Update the "Type Selection" table
 147 | 2. Add/update examples to illustrate the new type
 148 | 
 149 | ### When Adding Examples
 150 | 1. Each example should demonstrate a distinct commit pattern
 151 | 2. Keep examples realistic -- use actual AReaL module names
 152 | 3. Show both subject-only and subject+body+key-changes variants
 153 | 
 154 | ### Important Design Decisions
 155 | - This skill is ALWAYS loaded (not optional) -- keep it concise to
 156 |   minimize token overhead on every commit
 157 | - Scope inference is path-based, not content-based -- simpler and
 158 |   more deterministic
 159 | - "Multiple areas" -> omit scope rather than invent a new one
 160 | 
 161 | ================================================================================
 162 | -->
```


---
## .agents/skills/create-pr/SKILL.md

```
   1 | ---
   2 | name: create-pr
   3 | description: Rebase the current branch onto the latest base branch, squash local commits, generate a Conventional Commit message, and create or update the GitHub pull request.
   4 | ---
   5 | 
   6 | # Create Pull Request
   7 | 
   8 | Use this skill when the user asks to create or update a PR for the current branch.
   9 | 
  10 | ## Inputs
  11 | 
  12 | - Optional `--draft`
  13 | - Optional `--base <branch>` (default: `main`)
  14 | 
  15 | ## Preconditions
  16 | 
  17 | 1. Verify the current branch is not `main` or `master`.
  18 | 1. Check for uncommitted changes with `git status --short`.
  19 | 1. Ensure `gh` is available.
  20 | 1. If there are uncommitted changes, stop and ask the user whether to commit or stash
  21 |    them first.
  22 | 
  23 | ## Workflow
  24 | 
  25 | ### Step 1: Check for an existing PR
  26 | 
  27 | - Run `gh pr view --json number,title,url,state,isDraft`.
  28 | - If a PR already exists, tell the user before rewriting history or force-pushing.
  29 | 
  30 | ### Step 2: Fetch and rebase
  31 | 
  32 | ```bash
  33 | git fetch origin <base>
  34 | git rebase origin/<base>
  35 | ```
  36 | 
  37 | - If rebase conflicts occur, abort the rebase and stop.
  38 | - Tell the user which files conflicted and ask them to resolve manually.
  39 | 
  40 | ### Step 3: Squash into one commit
  41 | 
  42 | ```bash
  43 | git reset --soft origin/<base>
  44 | ```
  45 | 
  46 | - Load the `commit-conventions` skill before generating the commit message.
  47 | - Infer `type` and `scope` from the staged diff.
  48 | - Keep the commit subject imperative and under about 72 characters.
  49 | 
  50 | ### Step 4: Generate PR title and body
  51 | 
  52 | - Use the squashed commit message style for the PR title.
  53 | - Follow the repository PR template at `.github/PULL_REQUEST_TEMPLATE.md`.
  54 | - Summarize user-facing changes, risk areas, test commands run, and skipped suites with
  55 |   reasons.
  56 | 
  57 | ### Step 5: Push and create or update the PR
  58 | 
  59 | - Push the branch.
  60 | - If history was rewritten, confirm before force-pushing.
  61 | - Create or update the PR with `gh pr create` or `gh pr edit`.
  62 | - Respect `--draft` when requested.
  63 | 
  64 | ## Guardrails
  65 | 
  66 | - Never create a PR from `main` or `master`.
  67 | - Never silently force-push over an existing PR branch.
  68 | - Never bypass `commit-conventions` for the squashed commit.
  69 | - If `gh` authentication or remote permissions fail, stop and report the exact blocker.
  70 | 
  71 | ## Output
  72 | 
  73 | Report:
  74 | 
  75 | - Base branch used
  76 | - Final commit message
  77 | - PR title
  78 | - PR URL, if creation or update succeeded
  79 | - Any steps that were skipped or require user follow-up
```


---
## .agents/skills/debug-distributed/SKILL.md

```
   1 | ---
   2 | name: debug-distributed
   3 | description: Guide for debugging distributed training issues in AReaL. Use when user encounters hangs, wrong results, OOM, or communication errors.
   4 | ---
   5 | 
   6 | # Debug Distributed Training
   7 | 
   8 | Debugging guide for distributed training issues in AReaL (FSDP2, TP, CP, EP).
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - Training hangs or deadlocks
  15 | - Results differ across ranks or are numerically wrong
  16 | - OOM errors in distributed settings
  17 | - NCCL/communication errors or device mesh issues
  18 | 
  19 | ## Debugging Principles
  20 | 
  21 | ### Minimal Reproduction
  22 | 
  23 | **Always follow the minimal demo principle**: Reproduce with the least amount of code to
  24 | narrow down the issue faster.
  25 | 
  26 | ```python
  27 | # Bad: Debug in full training loop
  28 | # Good: Create minimal script
  29 | import torch
  30 | import torch.distributed as dist
  31 | 
  32 | dist.init_process_group("nccl")
  33 | rank = dist.get_rank()
  34 | 
  35 | # Reproduce the exact operation that fails
  36 | tensor = torch.ones(10).cuda()
  37 | dist.all_reduce(tensor)  # <-- Isolate the failing op
  38 | print(f"Rank {rank}: {tensor}")
  39 | ```
  40 | 
  41 | **Reduction strategy:**
  42 | 
  43 | 1. Remove unrelated model components
  44 | 1. Use small tensor sizes
  45 | 1. Reduce world_size to minimum (e.g., 2 GPUs)
  46 | 1. Remove torch.compile if possible
  47 | 1. Disable activation checkpointing
  48 | 
  49 | ## Step-by-Step Debugging Guide
  50 | 
  51 | ### 1. Hang Debugging (Deadlocks, Synchronization)
  52 | 
  53 | **Environment Variables for Debugging**:
  54 | 
  55 | ```bash
  56 | # Full debug logging
  57 | export TORCH_DISTRIBUTED_DEBUG=DETAIL
  58 | export NCCL_DEBUG=INFO
  59 | export NCCL_DEBUG_SUBSYS=ALL
  60 | 
  61 | # torch.compile debugging
  62 | export TORCH_LOGS="+dynamo,recompiles"
  63 | export TORCHDYNAMO_VERBOSE=1
  64 | ```
  65 | 
  66 | **Dump Call Stack with py-spy** (for hung processes):
  67 | 
  68 | ```bash
  69 | # Find process IDs
  70 | ps aux | grep python
  71 | 
  72 | # Dump call stack of specific rank
  73 | py-spy dump --pid <PID>
  74 | 
  75 | # Record flame graph for performance analysis
  76 | py-spy record -o profile.svg --pid <PID> --duration 30
  77 | ```
  78 | 
  79 | **Common Causes**:
  80 | 
  81 | 1. **Mismatched Collectives**: One rank calls `all_reduce`, another doesn't.
  82 | 1. **Wrong Process Group**: Using wrong group for collective.
  83 | 1. **Tensor Shape Mismatch**: Different shapes across ranks.
  84 | 
  85 | **Debug Steps**:
  86 | 
  87 | ```python
  88 | # Verify group membership
  89 | mesh = parallel_dims.get_mesh("dp_shard_cp")
  90 | group = mesh.get_group()
  91 | print(f"Rank {dist.get_rank()}: group size = {dist.get_world_size(group)}")
  92 | 
  93 | # Print shapes on all ranks
  94 | print(f"Rank {dist.get_rank()}: tensor.shape = {tensor.shape}")
  95 | dist.barrier()
  96 | ```
  97 | 
  98 | **Timeout Adjustment** (for debugging only):
  99 | 
 100 | ```python
 101 | from areal.engine.core.distributed import patch_dist_group_timeout
 102 | from datetime import timedelta
 103 | patch_dist_group_timeout(timedelta(minutes=30))
 104 | ```
 105 | 
 106 | ### 2. Wrong Results (Gradient, Reduction Issues)
 107 | 
 108 | **Check DTensor Placements**:
 109 | 
 110 | ```python
 111 | from torch.distributed.tensor import DTensor
 112 | if isinstance(param, DTensor):
 113 |     print(f"Param {name}: placements={param.placements}, mesh={param.device_mesh}")
 114 | ```
 115 | 
 116 | **Verify Gradient Reduction**:
 117 | 
 118 | ```python
 119 | for name, param in model.named_parameters():
 120 |     if param.grad is not None:
 121 |         print(f"Rank {dist.get_rank()}: {name} grad_sum = {param.grad.sum().item()}")
 122 | ```
 123 | 
 124 | ### 3. OOM Issues (Memory, Sharding)
 125 | 
 126 | **Check Memory Usage**:
 127 | 
 128 | ```python
 129 | print(f"Rank {dist.get_rank()}: "
 130 |       f"allocated={torch.cuda.memory_allocated()/1e9:.2f}GB, "
 131 |       f"reserved={torch.cuda.memory_reserved()/1e9:.2f}GB")
 132 | ```
 133 | 
 134 | **Check FSDP Coverage**:
 135 | 
 136 | ```python
 137 | for name, param in model.named_parameters():
 138 |     is_dtensor = isinstance(param, DTensor)
 139 |     print(f"{name}: is_dtensor={is_dtensor}, shape={param.shape}")
 140 | ```
 141 | 
 142 | ### 4. Communication Errors
 143 | 
 144 | | Error                     | Cause                | Solution                           |
 145 | | ------------------------- | -------------------- | ---------------------------------- |
 146 | | `NCCL WARN Cuda failure`  | GPU communication    | Check NCCL version, GPU topology   |
 147 | | `RuntimeError: Timed out` | Rank synchronization | Increase timeout, check code paths |
 148 | | `Invalid device mesh`     | Mesh configuration   | Verify world_size = dp * tp * cp   |
 149 | 
 150 | ## Debugging Tools
 151 | 
 152 | ### Environment Variables Reference
 153 | 
 154 | | Variable                          | Purpose                                |
 155 | | --------------------------------- | -------------------------------------- |
 156 | | `TORCH_DISTRIBUTED_DEBUG=DETAIL`  | Detailed distributed logging           |
 157 | | `NCCL_DEBUG=INFO`                 | NCCL communication logging             |
 158 | | `NCCL_DEBUG_SUBSYS=ALL`           | All NCCL subsystems                    |
 159 | | `TORCH_LOGS="+dynamo,recompiles"` | torch.compile logging                  |
 160 | | `TORCHDYNAMO_VERBOSE=1`           | Dynamo verbose output                  |
 161 | | `CUDA_LAUNCH_BLOCKING=1`          | Synchronous CUDA (slow, for debugging) |
 162 | 
 163 | ### py-spy for Call Stack Analysis
 164 | 
 165 | ```bash
 166 | # Install
 167 | pip install py-spy
 168 | 
 169 | # Dump call stack of hung process
 170 | py-spy dump --pid <PID>
 171 | 
 172 | # Dump all Python processes
 173 | pgrep -f python | xargs -I {} py-spy dump --pid {}
 174 | 
 175 | # Record flame graph
 176 | py-spy record -o profile.svg --pid <PID> --duration 30
 177 | ```
 178 | 
 179 | ### Rank-Conditional Printing
 180 | 
 181 | ```python
 182 | def print_all_ranks(msg):
 183 |     for r in range(dist.get_world_size()):
 184 |         if dist.get_rank() == r:
 185 |             print(f"[Rank {r}] {msg}")
 186 |         dist.barrier()
 187 | ```
 188 | 
 189 | ### Check Device Mesh
 190 | 
 191 | ```python
 192 | def debug_mesh(parallel_dims):
 193 |     mesh = parallel_dims.world_mesh
 194 |     for dim_name in mesh.mesh_dim_names:
 195 |         submesh = parallel_dims.get_mesh(dim_name)
 196 |         if submesh:
 197 |             print(f"Rank {dist.get_rank()}: {dim_name} size={submesh.size()}")
 198 | ```
 199 | 
 200 | ### Validate Tensor Consistency
 201 | 
 202 | ```python
 203 | def check_tensor_consistency(tensor, name, group=None):
 204 |     local_sum = tensor.sum().item()
 205 |     tensor_sums = [None] * dist.get_world_size(group)
 206 |     dist.all_gather_object(tensor_sums, local_sum, group=group)
 207 |     if dist.get_rank() == 0 and len(set(tensor_sums)) > 1:
 208 |         print(f"WARNING: {name} inconsistent: {tensor_sums}")
 209 | ```
 210 | 
 211 | ## Key Files Reference
 212 | 
 213 | | Component       | File                                                          |
 214 | | --------------- | ------------------------------------------------------------- |
 215 | | Parallel Dims   | `areal/experimental/models/archon/parallel_dims.py`           |
 216 | | Expert Parallel | `areal/experimental/models/archon/expert_parallel.py`         |
 217 | | Ulysses (CP)    | `areal/experimental/models/archon/ulysses.py`                 |
 218 | | FSDP/TP Apply   | `areal/experimental/models/archon/qwen2/infra/parallelize.py` |
```


---
## .agents/skills/review-pr/SKILL.md

```
   1 | ---
   2 | name: review-pr
   3 | description: Read-only pull request review workflow with risk analysis, targeted checklists, and Codex subagent consultation.
   4 | ---
   5 | 
   6 | # Review Pull Request
   7 | 
   8 | Use this skill when the user asks for a PR review of the current branch or a specific
   9 | PR.
  10 | 
  11 | ## Inputs
  12 | 
  13 | - Optional PR number
  14 | - Optional `--quick` to stop after the change analysis phase
  15 | 
  16 | ## Hard Rules
  17 | 
  18 | - Stay read-only.
  19 | - Do not edit files, commit, push, rebase, or change GitHub state.
  20 | - Do not run build, install, or test commands that mutate the environment.
  21 | - Use `gh` for PR metadata and git diff retrieval.
  22 | 
  23 | ## Reference Files
  24 | 
  25 | - `references/review-pr-change-types.md`
  26 | - `references/review-pr-templates.md`
  27 | 
  28 | ## Workflow
  29 | 
  30 | ### Phase 1: Resolve PR context
  31 | 
  32 | 1. Use `gh pr view` to fetch PR title, body, state, draft status, and changed files.
  33 | 1. If no PR exists, stop and report that clearly.
  34 | 1. If the PR is closed, stop.
  35 | 1. Record the branch name and changed file list.
  36 | 
  37 | ### Phase 2: Change analysis
  38 | 
  39 | 1. Classify changed files using `references/review-pr-change-types.md`.
  40 | 1. Determine the highest overall risk level: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`.
  41 | 1. Build a `CHANGE_ANALYSIS_REPORT` that lists:
  42 |    - detected change types
  43 |    - risk level
  44 |    - affected files
  45 |    - related frameworks
  46 |    - likely failure modes
  47 | 
  48 | If `--quick` is set, return the change analysis report and stop here.
  49 | 
  50 | ### Phase 3: Review planning
  51 | 
  52 | 1. Select the smallest useful set of review passes from
  53 |    `references/review-pr-templates.md`.
  54 | 1. Split by risk area, not by file count.
  55 | 1. Always include at least one general logic pass.
  56 | 
  57 | ### Phase 4: Expert consultation
  58 | 
  59 | Consult the matching Codex subagents registered in `.codex/config.toml` when relevant:
  60 | 
  61 | - `archon-expert`
  62 | - `fsdp-expert`
  63 | - `megatron-expert`
  64 | - `algorithm-expert`
  65 | - `launcher-expert`
  66 | 
  67 | If the Codex runtime supports parallel subagent execution, run independent review passes
  68 | in parallel. Otherwise, execute them serially.
  69 | 
  70 | ### Phase 5: Final review
  71 | 
  72 | Produce findings first, ordered by severity:
  73 | 
  74 | 1. `CRITICAL`
  75 | 1. `HIGH`
  76 | 1. `MEDIUM`
  77 | 1. `LOW`
  78 | 
  79 | For every finding, include:
  80 | 
  81 | - file path
  82 | - line number when available
  83 | - why it is a bug, regression, or risk
  84 | - concrete fix direction
  85 | 
  86 | ## What to Ignore
  87 | 
  88 | - Pure style nits with no correctness impact
  89 | - Issues outside the changed scope unless the PR makes them worse
  90 | - Failures that standard linters or formatters would already catch
  91 | - Speculative concerns with no concrete trigger in the diff
  92 | 
  93 | ## Output Shape
  94 | 
  95 | Use this structure:
  96 | 
  97 | ```markdown
  98 | CHANGE_ANALYSIS_REPORT:
  99 | - detected_types: [...]
 100 | - risk_level: ...
 101 | - affected_files: [...]
 102 | - related_frameworks: [...]
 103 | - identified_risks: [...]
 104 | 
 105 | Findings
 106 | 1. [severity] Title — path:line
 107 |    - Problem: ...
 108 |    - Fix: ...
 109 | 
 110 | Open Questions
 111 | - ...
 112 | 
 113 | Residual Risk
 114 | - ...
 115 | ```
```


---
## .agents/skills/translate-doc-zh/SKILL.md

```
   1 | ---
   2 | name: translate-doc-zh
   3 | description: Translate an English document under `docs/en/` into the matching Chinese document under `docs/zh/`.
   4 | ---
   5 | 
   6 | # Translate Docs EN to ZH
   7 | 
   8 | Use this skill when the user asks to translate a document from `docs/en/` to `docs/zh/`.
   9 | 
  10 | ## Input
  11 | 
  12 | - A markdown file path under `docs/en/`
  13 | 
  14 | ## Workflow
  15 | 
  16 | ### Step 1: Validate the source path
  17 | 
  18 | 1. Confirm the file exists.
  19 | 1. Confirm it is under `docs/en/`.
  20 | 1. Confirm it ends with `.md`.
  21 | 1. If any check fails, stop and ask the user for a valid `docs/en/...md` path.
  22 | 
  23 | ### Step 2: Resolve the target path
  24 | 
  25 | - Source: `docs/en/<path>.md`
  26 | - Target: `docs/zh/<path>.md`
  27 | 
  28 | ### Step 3: Choose translation mode
  29 | 
  30 | - If the Chinese file already exists, update only the changed parts while preserving the
  31 |   rest.
  32 | - If the Chinese file does not exist, translate the full document.
  33 | 
  34 | ## Translation Rules
  35 | 
  36 | - Preserve technical terms such as FSDP, FSDP2, GRPO, PPO, DAPO, MoE, LLM, RL, RLVR,
  37 |   Codex, Claude Code, OpenCode, Megatron, Archon, SGLang, vLLM, PyTorch, HuggingFace,
  38 |   and Transformers.
  39 | - Do not translate file paths, code blocks, CLI flags, or literal configuration keys.
  40 | - Preserve Markdown structure, tables, and fenced code blocks.
  41 | - Use concise, professional Chinese terminology.
  42 | 
  43 | ## Error Handling
  44 | 
  45 | - If the target directory does not exist, create it before writing the translated file.
  46 | - If the source document is partially translated already, preserve sections that do not
  47 |   need updates.
```


---
## .agents/skills/update-docker-image/SKILL.md

```
   1 | ---
   2 | name: update-docker-image
   3 | description: Update runtime dependency versions, validate Docker build compatibility, and drive the Docker image PR workflow.
   4 | ---
   5 | 
   6 | ## Usage
   7 | 
   8 | ```text
   9 | Input package versions: $VERSION
  10 | ```
  11 | 
  12 | **Arguments (`$VERSION`):** a list of pinned package versions, such as "sglang==0.5.9
  13 | vllm==0.10.1 torch==2.10.1"
  14 | 
  15 | ## Architecture
  16 | 
  17 | The Dockerfile produces two image variants from a single file:
  18 | 
  19 | - `ghcr.io/inclusionai/areal-runtime:{tag}-sglang` — SGLang inference backend
  20 | - `ghcr.io/inclusionai/areal-runtime:{tag}-vllm` — vLLM inference backend
  21 | 
  22 | Both variants share the same base image (`lmsysorg/sglang:…`) and identical layers up to
  23 | STAGE 3. Only `ARG VARIANT` (declared late for cache efficiency) controls which
  24 | inference backend is installed via `--extra ${VARIANT}`.
  25 | 
  26 | The `latest` tag always points to the sglang variant.
  27 | 
  28 | ## Workflow
  29 | 
  30 | 1. **Validate versions.** Update the version requirements in @pyproject.toml according
  31 |    to the input. Validate that the provided versions exist in the pip registry.
  32 |    Otherwise, exit and raise an error report to the user. Keep other dependency versions
  33 |    unchanged in this step.
  34 | 
  35 | 1. **Check upstream dependency compatibility.** For the following packages, browse the
  36 |    GitHub repo and check for dependency version mismatches with AReaL:
  37 | 
  38 |    - For sglang, check
  39 |      `https://github.com/sgl-project/sglang/blob/v${version}/python/pyproject.toml`
  40 |    - For vllm, check
  41 |      `https://github.com/vllm-project/vllm/blob/v${version}/pyproject.toml`
  42 | 
  43 |    Focus on the verions of following packages in particular:
  44 | 
  45 |    - torch
  46 |    - transformers
  47 | 
  48 | 1. **Resolve dependency conflicts** and report to user.
  49 | 
  50 |    If there's no inconsistency between the above packages, and it only conflicts with
  51 |    AReaL, update AReaL's version.
  52 | 
  53 |    If the above packages have mutual conflict, summarize and report to user, then you
  54 |    MUST ask the user for resolution.
  55 | 
  56 |    Output format:
  57 | 
  58 |    ```
  59 |    Summary
  60 | 
  61 |    ---
  62 |    Updated Packages (no actions required):
  63 |    - ${name}, ${packageA} requires ${packageAVersion}, ${packageB} requires ${packageBVersion}, AReaL specified ${version}, updated to ${version}
  64 |    - ...
  65 | 
  66 |    ---
  67 |    Mismatched Packages (need to resolve):
  68 | 
  69 |    - ${name}, ${packageA} requires ${packageAVersion}, ${packageB} requires ${packageBVersion}
  70 |    - ...
  71 |    ```
  72 | 
  73 | 1. **Update @pyproject.toml** according to the user's conflict resolution. You may use
  74 |    `override-dependencies` in `[tool.uv]` to force-pin versions where needed. Remember
  75 |    that `sglang` and `vllm` are declared as **conflicting extras** — never install both.
  76 | 
  77 | 1. **Validate** that the conflicts in step 3 have been all resolved. If not, return to
  78 |    step 3 and you MUST ask the user again.
  79 | 
  80 | 1. **Lock dependencies.** Run `uv lock` to regenerate `uv.lock`. If errors occur, return
  81 |    to step 3 — you must ask the user for resolution before modifying and trying again.
  82 | 
  83 | 1. **Update the Dockerfile** if needed. The Dockerfile uses only `ARG VARIANT` (no
  84 |    `ARG BASE_IMAGE`) to select between sglang and vllm. All layers before the VARIANT
  85 |    declaration are shared between both variants for Docker cache efficiency.
  86 | 
  87 |    Only modify the Dockerfile if the base image, system packages, or build steps need to
  88 |    change (e.g., new base image URL, new CUDA version). Do NOT modify it just for
  89 |    pyproject.toml version bumps — `uv pip install -r pyproject.toml` handles that
  90 |    automatically.
  91 | 
  92 | 1. **Create a PR and trigger CI.** Load the `create-pr` skill to create the PR, then
  93 |    trigger the CI workflow manually via `.github/workflows/build-docker-image.yml`.
  94 | 
  95 |    The docker build CI builds both sglang and vllm images, then automatically triggers
  96 |    testing on each. Debug until the overall workflow succeeds.
  97 | 
  98 |    If you encounter issues that cannot be resolved, ask the user for help.
```


---
## .agents/skills/upgrade-megatron-core/SKILL.md

```
   1 | ---
   2 | name: upgrade-megatron-core
   3 | description: Upgrade Megatron-Core in AReaL by auditing affected APIs, cross-referencing upstream sources, and updating call sites.
   4 | ---
   5 | 
   6 | ## Usage
   7 | 
   8 | ```text
   9 | Target Megatron-Core version: $VERSION
  10 | ```
  11 | 
  12 | **Arguments (`$VERSION`):** Target Megatron-Core version tag or commit hash, e.g.
  13 | `v0.12.0`, `core_r0.12.0`, or a commit SHA. If not given, get the required version from
  14 | AReaL's "pyproject.toml" and check whether the current code is fully compatible with the
  15 | specified version.
  16 | 
  17 | ## Prerequisites — Source Code for Cross-Referencing
  18 | 
  19 | This skill requires upstream source repos to cross-reference API signatures.
  20 | 
  21 | ### Megatron-LM
  22 | 
  23 | ```bash
  24 | MCORE_DIR="${REPO_ROOT}/Megatron-LM"
  25 | # Validate VERSION to prevent command injection
  26 | if [[ ! "$VERSION" =~ ^[a-zA-Z0-9._/-]+$ ]]; then
  27 |   echo "Error: Invalid version format: $VERSION"
  28 |   exit 1
  29 | fi
  30 | if [ ! -d "$MCORE_DIR" ]; then
  31 |   git clone --depth 1 --branch "${VERSION}" https://github.com/NVIDIA/Megatron-LM.git "$MCORE_DIR"
  32 | else
  33 |   cd "$MCORE_DIR" && git fetch origin && git checkout "${VERSION}" && cd -
  34 | fi
  35 | ```
  36 | 
  37 | If cloning or checkout fails, report to the user immediately.
  38 | 
  39 | The relevant upstream source paths are:
  40 | 
  41 | - `Megatron-LM/megatron/core/parallel_state.py`
  42 | - `Megatron-LM/megatron/core/distributed/`
  43 | - `Megatron-LM/megatron/core/optimizer/`
  44 | - `Megatron-LM/megatron/core/optimizer_param_scheduler.py`
  45 | - `Megatron-LM/megatron/core/pipeline_parallel/`
  46 | - `Megatron-LM/megatron/core/transformer/`
  47 | - `Megatron-LM/megatron/core/models/gpt/`
  48 | - `Megatron-LM/megatron/core/fp8_utils.py`
  49 | - `Megatron-LM/megatron/core/dist_checkpointing/`
  50 | - `Megatron-LM/megatron/core/packed_seq_params.py`
  51 | - `Megatron-LM/megatron/core/utils.py`
  52 | 
  53 | ### mbridge
  54 | 
  55 | mbridge wraps megatron.core for HF↔MCore weight conversion. AReaL depends on its
  56 | internal APIs for weight loading/saving, so mbridge must also be audited when upgrading
  57 | megatron-core.
  58 | 
  59 | ```bash
  60 | MBRIDGE_DIR="${REPO_ROOT}/mbridge-src"
  61 | # Determine the compatible mbridge version from pyproject.toml
  62 | MBRIDGE_VER=$(grep 'mbridge' "${REPO_ROOT}/pyproject.toml" | grep -oP '\d+\.\d+\.\d+')
  63 | if [ ! -d "$MBRIDGE_DIR" ]; then
  64 |   git clone --branch "v${MBRIDGE_VER}" https://github.com/ISEEKYAN/mbridge.git "$MBRIDGE_DIR"
  65 | else
  66 |   cd "$MBRIDGE_DIR" && git fetch origin && git checkout "v${MBRIDGE_VER}" && cd -
  67 | fi
  68 | ```
  69 | 
  70 | The relevant mbridge source paths are:
  71 | 
  72 | - `mbridge-src/mbridge/__init__.py` — top-level exports (`AutoBridge`)
  73 | - `mbridge-src/mbridge/core/bridge.py` — `Bridge` base class: `get_model()`,
  74 |   `load_weights()`, `save_weights()`, `export_weights()`, `set_extra_args()`, all
  75 |   `_weight_*` private methods
  76 | - `mbridge-src/mbridge/core/auto_bridge.py` — `AutoBridge.from_pretrained()`,
  77 |   `from_config()`
  78 | - `mbridge-src/mbridge/core/llm_bridge.py` — `LLMBridge`: `_build_base_config()`,
  79 |   `_get_gptmodel_args()`, `_get_transformer_layer_spec()`, `_model_provider()`
  80 | - `mbridge-src/mbridge/core/vlm_bridge.py` — `VLMBridge` (not directly used but may
  81 |   affect inheritance)
  82 | - `mbridge-src/mbridge/core/util.py` — `get_model()`, `unwrap_model()`,
  83 |   `broadcast_from_megatron_pp()`, `preprocess_packed_seqs()`,
  84 |   `postprocess_packed_seqs()`
  85 | - `mbridge-src/mbridge/core/parallel_states.py` — `ParallelStates` dataclass (wraps
  86 |   `mpu.*` getters)
  87 | - `mbridge-src/mbridge/utils/post_creation_callbacks.py` — `make_value_model()`,
  88 |   `freeze_moe_router()`
  89 | 
  90 | ______________________________________________________________________
  91 | 
  92 | ## Affected Files
  93 | 
  94 | ### Primary (engine layer — most likely to break)
  95 | 
  96 | | File                                                     | Imports                                                                                                                                                                                                           |
  97 | | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  98 | | `areal/engine/megatron_engine.py`                        | `parallel_state`, `tensor_parallel`, `DDP`, `finalize_model_grads`, `OptimizerConfig`, `get_megatron_optimizer`, `OptimizerParamScheduler`, `get_forward_backward_func`, `TransformerConfig`, `get_model_config`  |
  99 | | `areal/engine/megatron_utils/megatron.py`                | `parallel_state`, `is_float8tensor`, `TransformerConfig`, `get_transformer_layer_offset`                                                                                                                          |
 100 | | `areal/engine/megatron_utils/checkpointer.py`            | `dist_checkpointing`, `mpu`, `tensor_parallel`, `ShardedObject`, `get_default_load_sharded_strategy`, `get_default_save_sharded_strategy`, `FullyParallelLoadStrategyWrapper`, `FullyParallelSaveStrategyWrapper` |
 101 | | `areal/engine/megatron_utils/packed_context_parallel.py` | `parallel_state`, `PackedSeqParams`                                                                                                                                                                               |
 102 | | `areal/engine/megatron_utils/pipeline_parallel.py`       | `TransformerConfig`, `PipelineParallelLayerLayout`                                                                                                                                                                |
 103 | | `areal/engine/megatron_utils/fp8/tensor_helper.py`       | `is_float8tensor`                                                                                                                                                                                                 |
 104 | 
 105 | ### Secondary (model layer)
 106 | 
 107 | | File                                        | Imports                                                                                                                                                 |
 108 | | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
 109 | | `areal/models/mcore/registry.py`            | `tensor_parallel`, `DDP`, `MCoreDDPConfig`, `GPTModel`, `TransformerConfig`                                                                             |
 110 | | `areal/models/mcore/hf_load.py`             | `parallel_state`, `is_float8tensor`                                                                                                                     |
 111 | | `areal/models/mcore/hf_save.py`             | `parallel_state`, `is_float8tensor`                                                                                                                     |
 112 | | `areal/models/mcore/common.py`              | `TransformerConfig`                                                                                                                                     |
 113 | | `areal/models/mcore/qwen3.py`               | `get_gpt_decoder_block_spec`, `TransformerConfig`                                                                                                       |
 114 | | `areal/models/tree_attn/module_megatron.py` | `PackedSeqParams`, `TransformerConfig`, `SelfAttention`, `AttnMaskType`, `TransformerBlockSubmodules`, `TransformerLayer`, `TransformerLayerSubmodules` |
 115 | 
 116 | ### Tertiary (infra + tests — lower risk)
 117 | 
 118 | | File                                                | Imports                                                  |
 119 | | --------------------------------------------------- | -------------------------------------------------------- |
 120 | | `areal/infra/workflow_executor.py`                  | `parallel_state` (conditional import inside method)      |
 121 | | `tests/test_estimate_num_params.py`                 | `parallel_state`, `tensor_parallel`                      |
 122 | | `tests/fp8/engine_utils.py`                         | `parallel_state`                                         |
 123 | | `tests/fp8/model_hooks.py`                          | `parallel_state`                                         |
 124 | | `tests/fp8/test_fp8_rmsnorm.py`                     | `get_fp8_context`, `is_float8tensor`, `get_model_config` |
 125 | | `tests/torchrun/run_megatron_engine_distributed.py` | `parallel_state`                                         |
 126 | 
 127 | ### mbridge files (coupled with megatron.core)
 128 | 
 129 | | File                                        | mbridge Imports                                         |
 130 | | ------------------------------------------- | ------------------------------------------------------- |
 131 | | `areal/engine/megatron_engine.py`           | `mbridge.AutoBridge`                                    |
 132 | | `areal/models/mcore/registry.py`            | `mbridge.core.bridge.Bridge`                            |
 133 | | `areal/models/mcore/hf_load.py`             | `mbridge.core.bridge.Bridge`                            |
 134 | | `areal/models/mcore/hf_save.py`             | `mbridge.core.Bridge`, `mbridge.core.util.unwrap_model` |
 135 | | `areal/models/tree_attn/module_megatron.py` | `mbridge.core.LLMBridge`                                |
 136 | | `tests/test_estimate_num_params.py`         | `mbridge.AutoBridge`                                    |
 137 | 
 138 | ______________________________________________________________________
 139 | 
 140 | ## API Usage Catalog
 141 | 
 142 | For each function/class below, verify the call signature against the upstream source at
 143 | the target version. Focus on: **missing new required parameters**, **removed old
 144 | parameters**, **renamed parameters**, **changed return types**, and **changed method
 145 | signatures on returned objects**.
 146 | 
 147 | ### 1. `megatron.core.parallel_state` (aliased as `mpu`)
 148 | 
 149 | **Source:** `Megatron-LM/megatron/core/parallel_state.py`
 150 | 
 151 | #### `mpu.initialize_model_parallel(...)`
 152 | 
 153 | Called in `megatron_engine.py:186`:
 154 | 
 155 | ```python
 156 | mpu.initialize_model_parallel(
 157 |     tensor_model_parallel_size=...,
 158 |     pipeline_model_parallel_size=...,
 159 |     virtual_pipeline_model_parallel_size=...,
 160 |     use_sharp=False,
 161 |     order="tp-cp-ep-dp-pp",
 162 |     context_parallel_size=...,
 163 |     expert_model_parallel_size=...,
 164 |     expert_tensor_parallel_size=...,
 165 |     distributed_timeout_minutes=...,
 166 | )
 167 | ```
 168 | 
 169 | **Check:** New required params? Renamed params? New parallelism dimensions? Removed
 170 | `use_sharp`? Changed `order` format?
 171 | 
 172 | #### `mpu.destroy_model_parallel()`
 173 | 
 174 | Called in `megatron_engine.py:426` and `tests/test_estimate_num_params.py:60`.
 175 | Straightforward — check for new required params.
 176 | 
 177 | #### Rank/world-size getters
 178 | 
 179 | All of the following are called without arguments unless noted:
 180 | 
 181 | - `mpu.get_data_parallel_rank()` /
 182 |   `mpu.get_data_parallel_rank(with_context_parallel=True)`
 183 | - `mpu.get_data_parallel_world_size()`
 184 | - `mpu.get_data_parallel_group()` /
 185 |   `mpu.get_data_parallel_group(with_context_parallel=True)`
 186 | - `mpu.get_tensor_model_parallel_rank()`
 187 | - `mpu.get_tensor_model_parallel_world_size()`
 188 | - `mpu.get_tensor_model_parallel_group()`
 189 | - `mpu.get_pipeline_model_parallel_rank()`
 190 | - `mpu.get_pipeline_model_parallel_world_size()`
 191 | - `mpu.get_pipeline_model_parallel_group()`
 192 | - `mpu.get_pipeline_model_parallel_last_rank()`
 193 | - `mpu.get_context_parallel_world_size()`
 194 | - `mpu.get_context_parallel_rank()`
 195 | - `mpu.get_context_parallel_group()`
 196 | - `mpu.get_expert_model_parallel_group()`
 197 | - `mpu.get_expert_model_parallel_world_size()`
 198 | - `mpu.get_expert_model_parallel_rank()`
 199 | - `mpu.get_expert_tensor_parallel_world_size()`
 200 | - `mpu.get_expert_tensor_parallel_group()`
 201 | - `mpu.get_expert_tensor_parallel_rank()`
 202 | - `mpu.get_expert_data_parallel_group()`
 203 | - `mpu.get_expert_data_parallel_rank()`
 204 | - `mpu.get_expert_tensor_model_pipeline_parallel_group()`
 205 | - `mpu.get_tensor_and_data_parallel_group(with_context_parallel=True)`
 206 | - `mpu.get_virtual_pipeline_model_parallel_rank()`
 207 | - `mpu.get_virtual_pipeline_model_parallel_world_size()`
 208 | - `mpu.set_virtual_pipeline_model_parallel_rank(vpp_rank)`
 209 | - `mpu.is_initialized()`
 210 | 
 211 | **Check:** Any renamed? Any removed? Any new required keyword-only args? Return type
 212 | changes?
 213 | 
 214 | #### `mpu.is_pipeline_last_stage(...)`
 215 | 
 216 | Called in two forms:
 217 | 
 218 | ```python
 219 | mpu.is_pipeline_last_stage()
 220 | mpu.is_pipeline_last_stage(ignore_virtual=False, vp_stage=model_vp_stage)
 221 | ```
 222 | 
 223 | **Check:** `ignore_virtual` / `vp_stage` params still exist?
 224 | 
 225 | #### `mpu.RankGenerator(...)`
 226 | 
 227 | Called in `megatron_engine.py:912`:
 228 | 
 229 | ```python
 230 | mpu.RankGenerator(tp=..., ep=1, dp=..., pp=..., cp=..., order="tp-cp-ep-dp-pp", rank_offset=0)
 231 | ```
 232 | 
 233 | **Check:** Constructor signature. New params?
 234 | 
 235 | #### `mpu.create_group(ranks, timeout=, pg_options=, group_desc=)`
 236 | 
 237 | Called in `megatron_engine.py:924`.
 238 | 
 239 | **Check:** Signature and kwargs.
 240 | 
 241 | #### `mpu.get_nccl_options(name, nccl_comm_cfgs)`
 242 | 
 243 | Called in `megatron_engine.py:927`:
 244 | 
 245 | ```python
 246 | mpu.get_nccl_options("tp-cp-pp", {})
 247 | ```
 248 | 
 249 | **Check:** Signature change.
 250 | 
 251 | ______________________________________________________________________
 252 | 
 253 | ### 2. `megatron.core.tensor_parallel`
 254 | 
 255 | **Source:** `Megatron-LM/megatron/core/tensor_parallel/`
 256 | 
 257 | #### `tensor_parallel.model_parallel_cuda_manual_seed(seed)`
 258 | 
 259 | Called in `megatron_engine.py:200`, `tests/test_estimate_num_params.py:34`.
 260 | 
 261 | **Check:** Signature.
 262 | 
 263 | #### `tensor_parallel.get_cuda_rng_tracker()`
 264 | 
 265 | Called in `checkpointer.py:172,313`. Returns object with `.get_states()` and
 266 | `.set_states(states)` methods.
 267 | 
 268 | **Check:** Return type still has `get_states()`/`set_states()` methods?
 269 | 
 270 | #### `tensor_parallel.gather_from_sequence_parallel_region(logits, tensor_parallel_output_grad=False)`
 271 | 
 272 | Called in `registry.py:49-51`.
 273 | 
 274 | **Check:** `tensor_parallel_output_grad` kwarg still exists?
 275 | 
 276 | ______________________________________________________________________
 277 | 
 278 | ### 3. `megatron.core.distributed`
 279 | 
 280 | **Source:** `Megatron-LM/megatron/core/distributed/`
 281 | 
 282 | #### `DistributedDataParallel` (DDP)
 283 | 
 284 | Used in `megatron_engine.py` and `registry.py`.
 285 | 
 286 | Constructor called in `registry.py:199`:
 287 | 
 288 | ```python
 289 | DDP(config=tf_config, ddp_config=ddp_config, module=model, disable_bucketing=False)
 290 | ```
 291 | 
 292 | Methods/attributes used:
 293 | 
 294 | - `model_chunk.no_sync` (property/context manager)
 295 | - `model_chunk.start_param_sync` (method)
 296 | - `.zero_grad_buffer()` (called in `megatron_engine.py:543`)
 297 | - `.module` attribute
 298 | - `.vp_stage` attribute (set manually)
 299 | 
 300 | **Check:** Constructor params. `.zero_grad_buffer()` still exists? `no_sync` /
 301 | `start_param_sync` interface?
 302 | 
 303 | #### `DistributedDataParallelConfig` (as `MCoreDDPConfig`)
 304 | 
 305 | Used in `registry.py:198`:
 306 | 
 307 | ```python
 308 | MCoreDDPConfig(**dataclasses.asdict(mcore_config.ddp))
 309 | ```
 310 | 
 311 | **Check:** Dataclass fields. Used fields: `use_distributed_optimizer`,
 312 | `overlap_grad_reduce`, `overlap_param_gather`, `align_param_gather`.
 313 | 
 314 | #### `finalize_model_grads`
 315 | 
 316 | Used in `megatron_engine.py:357`:
 317 | 
 318 | ```python
 319 | model_config.finalize_model_grads_func = finalize_model_grads
 320 | ```
 321 | 
 322 | **Check:** Signature of `finalize_model_grads`. Is it still assigned as a function
 323 | reference to `model_config.finalize_model_grads_func`?
 324 | 
 325 | ______________________________________________________________________
 326 | 
 327 | ### 4. `megatron.core.optimizer`
 328 | 
 329 | **Source:** `Megatron-LM/megatron/core/optimizer/`
 330 | 
 331 | #### `OptimizerConfig` (as `MCoreOptimizerConfig`)
 332 | 
 333 | Constructed in `megatron_engine.py:948`:
 334 | 
 335 | ```python
 336 | MCoreOptimizerConfig(
 337 |     optimizer=..., lr=..., min_lr=..., weight_decay=...,
 338 |     bf16=..., fp16=...,
 339 |     adam_beta1=..., adam_beta2=..., adam_eps=...,
 340 |     use_distributed_optimizer=..., params_dtype=...,
 341 |     clip_grad=..., fp8_recipe=...,
 342 | )
 343 | ```
 344 | 
 345 | Plus post-construction field assignments (lines 963-978):
 346 | 
 347 | - `overlap_param_gather_with_optimizer_step`
 348 | - `use_precision_aware_optimizer`
 349 | - `main_grads_dtype`
 350 | - `main_params_dtype`
 351 | - `exp_avg_dtype`
 352 | - `exp_avg_sq_dtype`
 353 | 
 354 | **Check:** All fields still exist? New required fields? Renamed fields? `fp8_recipe`
 355 | type changed?
 356 | 
 357 | #### `get_megatron_optimizer(config, model_chunks)`
 358 | 
 359 | Called in `megatron_engine.py:980`:
 360 | 
 361 | ```python
 362 | self.optimizer = get_megatron_optimizer(mcore_opt_config, self.model)
 363 | ```
 364 | 
 365 | **Check:** Signature change — does it still accept `(config, model_chunks)`? Any new
 366 | required params (e.g., `model_parallel_config`)? Return type interface: `.step()` should
 367 | return `(update_successful, grad_norm, num_zeros)`, `.param_groups`, `.zero_grad()`,
 368 | `.get_loss_scale()`, `.sharded_state_dict(state_dict)`, `.load_state_dict(state_dict)`.
 369 | 
 370 | ______________________________________________________________________
 371 | 
 372 | ### 5. `megatron.core.optimizer_param_scheduler`
 373 | 
 374 | **Source:** `Megatron-LM/megatron/core/optimizer_param_scheduler.py`
 375 | 
 376 | #### `OptimizerParamScheduler`
 377 | 
 378 | Constructed in `megatron_engine.py:987`:
 379 | 
 380 | ```python
 381 | OptimizerParamScheduler(
 382 |     optimizer, init_lr=..., max_lr=..., min_lr=...,
 383 |     lr_warmup_steps=..., lr_decay_steps=..., lr_decay_style=...,
 384 |     start_wd=..., end_wd=..., wd_incr_steps=..., wd_incr_style="constant",
 385 | )
 386 | ```
 387 | 
 388 | Methods used: `.step(1)`, `.state_dict()`, `.load_state_dict(state_dict)`.
 389 | 
 390 | **Check:** Constructor params — any renamed or removed? New required params? `.step()`
 391 | accepts integer increment?
 392 | 
 393 | ______________________________________________________________________
 394 | 
 395 | ### 6. `megatron.core.pipeline_parallel`
 396 | 
 397 | **Source:** `Megatron-LM/megatron/core/pipeline_parallel/`
 398 | 
 399 | #### `get_forward_backward_func()`
 400 | 
 401 | Called in `megatron_engine.py:621`. Returns a callable invoked as:
 402 | 
 403 | ```python
 404 | forward_backward_func(
 405 |     forward_step_func=forward_step,
 406 |     data_iterator=data_iterator,
 407 |     model=...,
 408 |     num_microbatches=...,
 409 |     seq_length=...,
 410 |     micro_batch_size=...,
 411 |     forward_only=...,
 412 | )
 413 | ```
 414 | 
 415 | **Check:** Return type callable signature. `forward_step_func` expected signature:
 416 | `(batch_iter, model) -> (output, loss_func)`. Any new required params like
 417 | `collect_non_loss_data`, `first_val_step`, `config`?
 418 | 
 419 | ______________________________________________________________________
 420 | 
 421 | ### 7. `megatron.core.transformer`
 422 | 
 423 | **Source:** `Megatron-LM/megatron/core/transformer/`
 424 | 
 425 | #### `TransformerConfig`
 426 | 
 427 | Used everywhere as configuration dataclass. Created via `bridge.config` or explicitly in
 428 | `common.py:check_and_construct_configs`.
 429 | 
 430 | Fields accessed in AReaL code:
 431 | 
 432 | - `hidden_size`, `num_attention_heads`, `num_query_groups`, `kv_channels`
 433 | - `ffn_hidden_size`, `num_layers`
 434 | - `num_moe_experts`, `moe_ffn_hidden_size`, `moe_layer_freq`
 435 | - `moe_shared_expert_intermediate_size`, `moe_router_enable_expert_bias`
 436 | - `expert_model_parallel_size`
 437 | - `sequence_parallel`, `context_parallel_size`
 438 | - `params_dtype`, `pipeline_dtype`, `bf16`, `fp16`
 439 | - `fp8`, `fp8_param`, `fp8_recipe`, and other `fp8_*` fields
 440 | - `gated_linear_unit`, `add_bias_linear`
 441 | - `deterministic_mode`, `cross_entropy_loss_fusion`, `bias_dropout_fusion`
 442 | - `no_sync_func`, `param_sync_func`, `finalize_model_grads_func`
 443 | - `variable_seq_lengths`, `masked_softmax_fusion`
 444 | - `pipeline_model_parallel_layout`
 445 | - `num_layers_in_first_pipeline_stage`, `num_layers_in_last_pipeline_stage`
 446 | - `account_for_embedding_in_pipeline_split`, `account_for_loss_in_pipeline_split`
 447 | 
 448 | **Check:** `check_and_construct_configs()` in `common.py` already handles removed fields
 449 | gracefully. But verify new required fields that may not have defaults.
 450 | 
 451 | #### `TransformerBlockSubmodules`, `TransformerLayer`, `TransformerLayerSubmodules`
 452 | 
 453 | Used in `module_megatron.py` for tree attention patching. Accessed via:
 454 | 
 455 | ```python
 456 | spec.layer_specs  # list of layer specs
 457 | layer_spec.module  # should be TransformerLayer
 458 | layer_spec.submodules  # TransformerLayerSubmodules
 459 | submodules.self_attention  # attention spec
 460 | self_attn_spec.module  # should be SelfAttention
 461 | self_attn_spec.params["attn_mask_type"] = AttnMaskType.arbitrary
 462 | self_attn_spec.submodules.core_attention = PytorchFlexAttention
 463 | ```
 464 | 
 465 | **Check:** `.layer_specs`, `.submodules`, `.self_attention`, `.params`,
 466 | `.submodules.core_attention` still exist on these objects?
 467 | 
 468 | #### `SelfAttention`
 469 | 
 470 | Used as a class reference check in `module_megatron.py:203`. Not instantiated directly.
 471 | 
 472 | **Check:** Still exists at `megatron.core.transformer.attention.SelfAttention`?
 473 | 
 474 | #### `AttnMaskType`
 475 | 
 476 | Used: `AttnMaskType.arbitrary` in `module_megatron.py:206`.
 477 | 
 478 | **Check:** `.arbitrary` enum value still exists?
 479 | 
 480 | #### `get_transformer_layer_offset(config, vp_stage=)`
 481 | 
 482 | Called in `megatron.py:612`:
 483 | 
 484 | ```python
 485 | layer_offset = get_transformer_layer_offset(config, vp_stage=vp_stage)
 486 | ```
 487 | 
 488 | **Check:** Signature.
 489 | 
 490 | #### `PipelineParallelLayerLayout`
 491 | 
 492 | Constructed in `pipeline_parallel.py:62`:
 493 | 
 494 | ```python
 495 | PipelineParallelLayerLayout(layout=layout, pipeline_model_parallel_size=pp_size)
 496 | ```
 497 | 
 498 | **Check:** Constructor params.
 499 | 
 500 | ______________________________________________________________________
 501 | 
 502 | ### 8. `megatron.core.models.gpt`
 503 | 
 504 | **Source:** `Megatron-LM/megatron/core/models/gpt/`
 505 | 
 506 | #### `GPTModel`
 507 | 
 508 | Constructed in `registry.py:179`:
 509 | 
 510 | ```python
 511 | GPTModel(
 512 |     config=tf_config, transformer_layer_spec=..., vocab_size=...,
 513 |     max_sequence_length=..., pre_process=True, post_process=True,
 514 |     share_embeddings_and_output_weights=False,
 515 |     position_embedding_type="rope", rotary_base=...,
 516 | )
 517 | ```
 518 | 
 519 | Attributes/methods used: `.output_layer`, `.vocab_size`, `.sharded_state_dict()`,
 520 | `.config`, `.module`, `.named_parameters()`, `.load_state_dict()`, `.state_dict()`.
 521 | 
 522 | **Check:** Constructor signature. `position_embedding_type` values. New required params?
 523 | 
 524 | #### `get_gpt_decoder_block_spec(config, use_transformer_engine=True)`
 525 | 
 526 | Called in `qwen3.py:32`:
 527 | 
 528 | ```python
 529 | get_gpt_decoder_block_spec(tfconfig, use_transformer_engine=use_te)
 530 | ```
 531 | 
 532 | **Check:** Signature. Was it renamed? Does it accept the same args?
 533 | 
 534 | ______________________________________________________________________
 535 | 
 536 | ### 9. `megatron.core.fp8_utils`
 537 | 
 538 | **Source:** `Megatron-LM/megatron/core/fp8_utils.py`
 539 | 
 540 | #### `is_float8tensor(param)`
 541 | 
 542 | Called in `megatron.py:83`, `tensor_helper.py:4`, `hf_load.py:12`, `hf_save.py:13`,
 543 | `test_fp8_rmsnorm.py:15`.
 544 | 
 545 | **Check:** Still exists? Signature unchanged?
 546 | 
 547 | #### `get_fp8_context()`
 548 | 
 549 | Called in `test_fp8_rmsnorm.py:15`.
 550 | 
 551 | **Check:** Signature.
 552 | 
 553 | ______________________________________________________________________
 554 | 
 555 | ### 10. `megatron.core.dist_checkpointing`
 556 | 
 557 | **Source:** `Megatron-LM/megatron/core/dist_checkpointing/`
 558 | 
 559 | #### `dist_checkpointing.save(...)`
 560 | 
 561 | Called in `checkpointer.py:60`:
 562 | 
 563 | ```python
 564 | dist_checkpointing.save(
 565 |     sharded_state_dict, ckpt_path,
 566 |     sharded_strategy=save_strategy,
 567 |     async_sharded_save=async_save,
 568 |     validate_access_integrity=validate_sharding_integrity,
 569 | )
 570 | ```
 571 | 
 572 | **Check:** `async_sharded_save` renamed? `validate_access_integrity` still exists?
 573 | 
 574 | #### `dist_checkpointing.load(...)`
 575 | 
 576 | Called in `checkpointer.py:79`:
 577 | 
 578 | ```python
 579 | dist_checkpointing.load(sharded_state_dict, ckpt_dir, sharded_strategy=load_strategy)
 580 | ```
 581 | 
 582 | **Check:** Signature.
 583 | 
 584 | #### `ShardedObject(key, data, global_shape, global_offset, replica_id=)`
 585 | 
 586 | Called in `checkpointer.py:198`.
 587 | 
 588 | **Check:** Constructor params.
 589 | 
 590 | #### Serialization strategies
 591 | 
 592 | ```python
 593 | get_default_load_sharded_strategy(ckpt_dir)
 594 | get_default_save_sharded_strategy("torch_dist")
 595 | FullyParallelLoadStrategyWrapper(load_strategy, group)
 596 | FullyParallelSaveStrategyWrapper(save_strategy, group)
 597 | ```
 598 | 
 599 | **Check:** All four still exist? Signatures unchanged?
 600 | 
 601 | ______________________________________________________________________
 602 | 
 603 | ### 11. `megatron.core.packed_seq_params`
 604 | 
 605 | **Source:** `Megatron-LM/megatron/core/packed_seq_params.py`
 606 | 
 607 | #### `PackedSeqParams`
 608 | 
 609 | Constructed in `packed_context_parallel.py:34`:
 610 | 
 611 | ```python
 612 | PackedSeqParams(
 613 |     qkv_format="thd",
 614 |     cu_seqlens_q=cu_seqlens, max_seqlen_q=max_seqlen,
 615 |     cu_seqlens_kv=cu_seqlens, max_seqlen_kv=max_seqlen,
 616 |     cu_seqlens_q_padded=cu_seqlens, cu_seqlens_kv_padded=cu_seqlens,
 617 | )
 618 | ```
 619 | 
 620 | **Check:** Constructor fields.
 621 | 
 622 | ______________________________________________________________________
 623 | 
 624 | ### 12. `megatron.core.utils`
 625 | 
 626 | **Source:** `Megatron-LM/megatron/core/utils.py`
 627 | 
 628 | #### `get_model_config(model)`
 629 | 
 630 | Called in `megatron_engine.py:326`, `test_fp8_rmsnorm.py:16`.
 631 | 
 632 | **Check:** Signature. Return type. What fields are expected on the returned config
 633 | object (`.no_sync_func`, `.param_sync_func`, `.finalize_model_grads_func`,
 634 | `.deterministic_mode`, `.cross_entropy_loss_fusion`, `.bias_dropout_fusion`)?
 635 | 
 636 | ______________________________________________________________________
 637 | 
 638 | ## Upgrade Workflow
 639 | 
 640 | ### Step 0: Prepare Megatron-LM source
 641 | 
 642 | Clone or checkout the target version as described in Prerequisites above.
 643 | 
 644 | ### Step 1: Audit `megatron.core` API signatures
 645 | 
 646 | For EACH entry in the API Usage Catalog above:
 647 | 
 648 | 1. Open the upstream source file at the target version.
 649 | 1. Compare the function/class signature against the current AReaL invocation.
 650 | 1. Flag any of:
 651 |    - **Removed parameters** still passed by AReaL → must remove from call site
 652 |    - **Renamed parameters** → must rename in call site
 653 |    - **New required parameters** (no default) → must add to call site
 654 |    - **New optional parameters** with useful defaults → document but skip
 655 |    - **Changed return types** → must update consumers
 656 |    - **Removed functions/classes** → must find replacement
 657 |    - **Changed method signatures** on returned objects → must update call sites
 658 | 1. Record findings per-file.
 659 | 
 660 | ### Step 2: Audit `mbridge` compatibility
 661 | 
 662 | mbridge wraps megatron.core and may also need updates. Cross-reference the cloned
 663 | `mbridge-src/` repo to verify each API AReaL depends on.
 664 | 
 665 | #### 2a. Public API (used directly by AReaL)
 666 | 
 667 | | AReaL Call Site                     | mbridge API                                                                           | Source File to Check                                                                                      |
 668 | | ----------------------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
 669 | | `megatron_engine.py:242`            | `AutoBridge.from_pretrained(path)`                                                    | `mbridge-src/mbridge/core/auto_bridge.py` — `from_pretrained()` resolves model type via `_MODEL_REGISTRY` |
 670 | | `registry.py:139`                   | `bridge.get_model(wrap_with_ddp=..., ddp_config=..., use_torch_fsdp2=..., ...)`       | `mbridge-src/mbridge/core/bridge.py` — `get_model()` passes kwargs to `get_model()` util                  |
 671 | | `megatron_engine.py`                | `bridge.load_weights(model, path)`                                                    | `mbridge-src/mbridge/core/bridge.py` — `load_weights()`                                                   |
 672 | | `megatron_engine.py`                | `bridge.save_weights(models, path, memory_efficient=..., distributed_filesystem=...)` | `mbridge-src/mbridge/core/bridge.py` — `save_weights()` and `_save_weights_fast()`                        |
 673 | | `megatron_engine.py`                | `bridge.export_weights(models)`                                                       | `mbridge-src/mbridge/core/bridge.py` — `export_weights()` generator                                       |
 674 | | `megatron_engine.py`                | `bridge.set_extra_args(**kwargs)`                                                     | `mbridge-src/mbridge/core/bridge.py` — rebuilds `self.config`                                             |
 675 | | `registry.py`, `megatron_engine.py` | `bridge.config` (returns `TransformerConfig`)                                         | `mbridge-src/mbridge/core/llm_bridge.py` — `_build_base_config()` constructs the config                   |
 676 | | `registry.py`, `hf_save.py`         | `bridge.hf_config`                                                                    | Stored on `Bridge.__init__()` from HF `AutoConfig`                                                        |
 677 | 
 678 | **Check:** Do `get_model()` kwargs still match `bridge.py:get_model()` signature? Does
 679 | `_build_base_config()` in `llm_bridge.py` pass any new required fields to
 680 | `TransformerConfig`? Does `set_extra_args()` still call `_build_config()`?
 681 | 
 682 | #### 2b. Private/internal API (used by AReaL's custom weight loaders)
 683 | 
 684 | | AReaL Call Site  | mbridge Private API                                                           | Source File to Check                                                                            |
 685 | | ---------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
 686 | | `hf_load.py:396` | `bridge._weight_name_mapping_mcore_local_to_global(model)`                    | `mbridge-src/mbridge/core/bridge.py` — maps VPP+EP local names to global                        |
 687 | | `hf_load.py:399` | `bridge._weight_name_mapping_mcore_to_hf(global_name)`                        | `mbridge-src/mbridge/core/bridge.py` — dispatches to `_weight_name_mapping_attention/mlp/other` |
 688 | | `hf_save.py:376` | `bridge._weight_to_hf_format(global_name, infer_params)`                      | `mbridge-src/mbridge/core/bridge.py` — splits QKV/gate-up, returns `(names, tensors)`           |
 689 | | `hf_save.py:368` | `bridge._weight_merge_across_tp(name, params, param)`                         | `mbridge-src/mbridge/core/bridge.py` — merges TP-split tensors                                  |
 690 | | `hf_load.py:365` | `bridge._get_actual_hf_path(weights_path)`                                    | `mbridge-src/mbridge/core/bridge.py` or subclass — resolves HF cache paths                      |
 691 | | `hf_save.py:197` | `bridge._weight_name_mapping_mcore_local_to_global(model, consider_ep=False)` | Same as above but with `consider_ep` kwarg                                                      |
 692 | | `hf_save.py:452` | `bridge.config.num_moe_experts`                                               | Field on `TransformerConfig` built by `_build_base_config()`                                    |
 693 | | `hf_save.py:536` | `bridge.hf_config.save_pretrained(weights_path)`                              | Standard HF `PretrainedConfig` method                                                           |
 694 | | `hf_save.py:191` | `unwrap_model(model)` from `mbridge.core.util`                                | `mbridge-src/mbridge/core/util.py` — unwraps DDP/Float16Module/FSDP wrappers                    |
 695 | 
 696 | **Check:** Do any of these private methods have changed signatures? Has the weight name
 697 | mapping logic changed (e.g., new `_DIRECT_MAPPING`, `_ATTENTION_MAPPING`, or
 698 | `_MLP_MAPPING` entries)? Does `unwrap_model()` still handle the same wrapper classes?
 699 | 
 700 | #### 2c. `LLMBridge._get_transformer_layer_spec()` (monkey-patched by tree attention)
 701 | 
 702 | | AReaL Call Site              | mbridge API                                             | Source File to Check                                                            |
 703 | | ---------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------- |
 704 | | `module_megatron.py:193,211` | `LLMBridge._get_transformer_layer_spec(self, vp_stage)` | `mbridge-src/mbridge/core/llm_bridge.py` — calls `get_gpt_decoder_block_spec()` |
 705 | 
 706 | AReaL monkey-patches this method to inject `PytorchFlexAttention` as `core_attention`.
 707 | The patch accesses `spec.layer_specs[i].submodules.self_attention.params` and
 708 | `spec.layer_specs[i].submodules.self_attention.submodules.core_attention`.
 709 | 
 710 | **Check:** Does `_get_transformer_layer_spec()` still return a
 711 | `TransformerBlockSubmodules` with `.layer_specs` list? Does each layer spec still have
 712 | `.submodules.self_attention.params` dict and `.submodules.core_attention` attribute? Has
 713 | the `vp_stage` parameter been added/removed?
 714 | 
 715 | #### 2d. mbridge version compatibility
 716 | 
 717 | If mbridge also needs a version bump to work with the new megatron-core, note the
 718 | compatible mbridge version. Check `mbridge-src/pyproject.toml` for its megatron-core
 719 | version pin.
 720 | 
 721 | ### Step 3: Update `pyproject.toml`
 722 | 
 723 | Update the `megatron-core` (and optionally `mbridge`) version pin in `pyproject.toml`.
 724 | Run `uv lock` to verify dependency resolution.
 725 | 
 726 | ### Step 4: Apply code changes
 727 | 
 728 | For each flagged incompatibility from Steps 1-2:
 729 | 
 730 | 1. Update the call site in the affected file.
 731 | 1. Preserve existing behavior — do NOT refactor beyond what's required.
 732 | 1. If a function was removed, check the upstream migration guide or changelog.
 733 | 1. If a mbridge API changed (Step 2b/2c), update AReaL's usage to match the new mbridge
 734 |    signatures. Common cases:
 735 |    - `bridge.get_model()` gained/lost kwargs → update `registry.py:139`
 736 |    - `bridge._weight_*` private methods renamed or re-signed → update `hf_load.py` and
 737 |      `hf_save.py` callers
 738 |    - `LLMBridge._get_transformer_layer_spec()` return structure changed → update the
 739 |      monkey-patch in `module_megatron.py`
 740 |    - `unwrap_model()` wrapper class list changed → verify unwrapping still works
 741 | 
 742 | Priority order for applying changes:
 743 | 
 744 | 1. `areal/engine/megatron_engine.py` (highest risk, most API surface)
 745 | 1. `areal/engine/megatron_utils/megatron.py`
 746 | 1. `areal/engine/megatron_utils/checkpointer.py`
 747 | 1. `areal/engine/megatron_utils/packed_context_parallel.py`
 748 | 1. `areal/engine/megatron_utils/pipeline_parallel.py`
 749 | 1. `areal/engine/megatron_utils/fp8/tensor_helper.py`
 750 | 1. `areal/models/mcore/registry.py`
 751 | 1. `areal/models/mcore/common.py`
 752 | 1. `areal/models/mcore/qwen3.py`
 753 | 1. `areal/models/mcore/hf_load.py` (mbridge private API consumer)
 754 | 1. `areal/models/mcore/hf_save.py` (mbridge private API consumer)
 755 | 1. `areal/models/tree_attn/module_megatron.py` (mbridge monkey-patch)
 756 | 1. Test files
 757 | 
 758 | ### Step 5: Verify `TransformerConfig` field compatibility
 759 | 
 760 | `areal/models/mcore/common.py` uses `check_and_construct_configs()` which automatically
 761 | removes unsupported fields. However:
 762 | 
 763 | 1. Check that no **new required fields** (without defaults) were added to
 764 |    `TransformerConfig`.
 765 | 1. Verify `hf_to_mcore_base_args()` in `common.py` — the hardcoded field names
 766 |    (`num_layers`, `hidden_size`, etc.) still match.
 767 | 1. Check if `FP8`-related fields on `TransformerConfig` changed (used in
 768 |    `megatron_engine.py:_check_and_apply_fp8_config()`).
 769 | 
 770 | ### Step 6: Run pre-commit and tests
 771 | 
 772 | ```bash
 773 | pre-commit run --all-files
 774 | uv run pytest tests/test_estimate_num_params.py -v
 775 | ```
 776 | 
 777 | If GPU is available:
 778 | 
 779 | ```bash
 780 | uv run pytest tests/fp8/ -v
 781 | ```
 782 | 
 783 | ### Step 7: Report changes
 784 | 
 785 | Output a summary in this format:
 786 | 
 787 | ```
 788 | ## Upgrade Summary: megatron-core ${OLD_VERSION} → ${NEW_VERSION}
 789 | 
 790 | ### Breaking Changes Found
 791 | - [file:line] description of change needed
 792 | 
 793 | ### mbridge Compatibility
 794 | - mbridge version: ${MBRIDGE_VERSION} (compatible / needs bump to X.Y.Z)
 795 | - mbridge API changes affecting AReaL: (list or "none")
 796 | 
 797 | ### API Additions (new optional params, informational)
 798 | - [upstream_file] description
 799 | 
 800 | ### Files Modified
 801 | - path/to/file.py: description of change
 802 | 
 803 | ### Tests
 804 | - ✅ pre-commit passed
 805 | - ✅ test_estimate_num_params passed
 806 | - ⬚ FP8 tests (requires GPU)
 807 | ```
 808 | 
 809 | If there are unresolvable breaking changes, STOP and ask the user before proceeding.
```


---
## .agents/skills/upgrade-vllm/SKILL.md

```
   1 | ---
   2 | name: upgrade-vllm
   3 | description: Upgrade vLLM in AReaL by auditing affected APIs, cross-referencing upstream sources, and updating call sites.
   4 | ---
   5 | 
   6 | ## Usage
   7 | 
   8 | ```text
   9 | Target vLLM version: $VERSION
  10 | ```
  11 | 
  12 | **Arguments (`$VERSION`):** Target vLLM version tag or commit hash, e.g. `v0.18.0`,
  13 | `0.17.0`, or a commit SHA. If not given, get the required version from AReaL's
  14 | "pyproject.toml" and check whether the current code is fully compatible with the
  15 | specified version.
  16 | 
  17 | ## Prerequisites — Source Code for Cross-Referencing
  18 | 
  19 | This skill requires the upstream vLLM source repo to cross-reference API signatures.
  20 | 
  21 | ### vLLM
  22 | 
  23 | ```bash
  24 | VLLM_DIR="${REPO_ROOT}/vllm-src"
  25 | # Validate VERSION to prevent command injection
  26 | if [[ ! "$VERSION" =~ ^[a-zA-Z0-9._/-]+$ ]]; then
  27 |   echo "Error: Invalid version format: $VERSION"
  28 |   exit 1
  29 | fi
  30 | if [ ! -d "$VLLM_DIR" ]; then
  31 |   git clone --depth 1 --branch "${VERSION}" https://github.com/vllm-project/vllm.git "$VLLM_DIR"
  32 | else
  33 |   cd "$VLLM_DIR" && git fetch origin && git checkout "${VERSION}" && cd -
  34 | fi
  35 | ```
  36 | 
  37 | If cloning or checkout fails, report to the user immediately.
  38 | 
  39 | The relevant upstream source paths are:
  40 | 
  41 | - `vllm-src/vllm/entrypoints/openai/api_server.py`
  42 | - `vllm-src/vllm/entrypoints/openai/cli_args.py`
  43 | - `vllm-src/vllm/entrypoints/openai/completion/api_router.py`
  44 | - `vllm-src/vllm/entrypoints/openai/completion/protocol.py`
  45 | - `vllm-src/vllm/entrypoints/openai/engine/protocol.py`
  46 | - `vllm-src/vllm/entrypoints/openai/utils.py`
  47 | - `vllm-src/vllm/entrypoints/utils.py`
  48 | - `vllm-src/vllm/logger.py`
  49 | - `vllm-src/vllm/lora/request.py`
  50 | - `vllm-src/vllm/utils/argparse_utils.py`
  51 | - `vllm-src/vllm/v1/engine/__init__.py`
  52 | - `vllm-src/vllm/v1/engine/core.py`
  53 | - `vllm-src/vllm/v1/engine/output_processor.py`
  54 | - `vllm-src/vllm/v1/metrics/stats.py`
  55 | - `vllm-src/vllm/v1/request.py`
  56 | - `vllm-src/vllm/v1/worker/gpu_worker.py`
  57 | - `vllm-src/vllm/worker/worker.py`
  58 | - `vllm-src/vllm/lora/lora_model.py`
  59 | - `vllm-src/vllm/lora/peft_helper.py`
  60 | - `vllm-src/vllm/model_executor/model_loader/__init__.py`
  61 | - `vllm-src/vllm/envs.py`
  62 | 
  63 | ______________________________________________________________________
  64 | 
  65 | ## Affected Files
  66 | 
  67 | ### Primary (engine layer — most likely to break)
  68 | 
  69 | | File                                             | Imports / Usage                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
  70 | | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  71 | | `areal/engine/vllm_ext/areal_vllm_server.py`     | `entrypoints.openai.api_server` (`build_app`, `run_server`), `entrypoints.openai.cli_args`, `entrypoints.openai.completion.api_router` (`create_completion`), `entrypoints.openai.completion.protocol` (`CompletionRequest`), `entrypoints.openai.engine.protocol` (`ErrorResponse`, `OpenAIBaseModel`), `entrypoints.openai.utils` (`validate_json_request`), `entrypoints.utils`, `logger`, `lora.request`, `utils.argparse_utils`, `v1.engine`, `v1.engine.core`, `v1.metrics.stats`, `v1.request`, `v1.engine.output_processor` |
  72 | | `areal/engine/vllm_ext/vllm_worker_extension.py` | `logger`, `lora.lora_model`, `lora.peft_helper`, `lora.request`, `model_executor.model_loader`                                                                                                                                                                                                                                                                                                                                                                                                                                      |
  73 | | `areal/engine/vllm_remote.py`                    | `VLLMBackend` class (builds HTTP requests to vLLM endpoints), `RemotevLLMEngine` wrapper                                                                                                                                                                                                                                                                                                                                                                                                                                            |
  74 | 
  75 | ### Secondary (infrastructure / platform layer)
  76 | 
  77 | | File                                  | Imports / Usage                                                                                            |
  78 | | ------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
  79 | | `areal/infra/platforms/cuda.py`       | `vllm.v1.worker.gpu_worker.Worker` (try), `vllm.worker.worker.Worker` (fallback) via try/except            |
  80 | | `areal/infra/platforms/unknown.py`    | Same as `cuda.py`                                                                                          |
  81 | | `areal/infra/platforms/platform.py`   | Abstract `get_vllm_worker_class()` method                                                                  |
  82 | | `areal/infra/launcher/vllm_server.py` | `vLLMServerWrapper`, `launch_server_cmd`, env vars (`VLLM_CACHE_ROOT`, `VLLM_ALLOW_RUNTIME_LORA_UPDATING`) |
  83 | | `areal/infra/launcher/ray.py`         | vLLM server launch in Ray cluster (imports `vLLMConfig`)                                                   |
  84 | | `areal/infra/launcher/local.py`       | vLLM server launch locally (imports `vLLMConfig`)                                                          |
  85 | | `areal/infra/launcher/slurm.py`       | vLLM server launch in Slurm (imports `vLLMConfig`)                                                         |
  86 | | `areal/infra/launcher/__init__.py`    | Re-exports `launch_vllm_server`, `vLLMServerWrapper`                                                       |
  87 | | `areal/infra/utils/launcher.py`       | `VLLM_CACHE_ROOT` path, vLLM allocation mode validation                                                    |
  88 | 
  89 | ### Tertiary (config / API / workflow layer)
  90 | 
  91 | | File                                          | Usage                                                            |
  92 | | --------------------------------------------- | ---------------------------------------------------------------- |
  93 | | `areal/api/cli_args.py`                       | `vLLMConfig` dataclass — all vLLM CLI flags and server arguments |
  94 | | `areal/api/alloc_mode.py`                     | `"vllm"` as a backend literal type                               |
  95 | | `areal/api/io_struct.py`                      | `vision_msg_vllm` field on `ModelRequest`                        |
  96 | | `areal/trainer/rl_trainer.py`                 | `RemotevLLMEngine` initialization, `vLLMConfig.build_args()`     |
  97 | | `areal/workflow/vision_rlvr.py`               | Sets `vision_msg_vllm` on `ModelRequest`                         |
  98 | | `areal/tools/validate_docker_installation.py` | Checks `vllm` is importable, validates `vllm._C`                 |
  99 | | `areal/tools/validation_base.py`              | `vllm._C` as native extension verification                       |
 100 | 
 101 | ### Test files
 102 | 
 103 | | File                              | Usage                                                      |
 104 | | --------------------------------- | ---------------------------------------------------------- |
 105 | | `tests/test_inference_engines.py` | `vLLMConfig`, `RemotevLLMEngine`, engine integration tests |
 106 | | `tests/test_model_utils.py`       | vLLM allocation mode regression tests                      |
 107 | | `tests/test_allocation_mode.py`   | vLLM allocation mode parsing tests                         |
 108 | | `tests/test_examples.py`          | vLLM integration test configurations                       |
 109 | | `tests/grpo/test_grpo.py`         | vLLM references in GRPO config tests                       |
 110 | 
 111 | ______________________________________________________________________
 112 | 
 113 | ## API Usage Catalog
 114 | 
 115 | For each function/class below, verify the call signature against the upstream source at
 116 | the target version. Focus on: **missing new required parameters**, **removed old
 117 | parameters**, **renamed parameters**, **changed return types**, **changed method
 118 | signatures on returned objects**, and **moved/renamed modules**.
 119 | 
 120 | ### 1. `vllm.entrypoints.openai.api_server`
 121 | 
 122 | **Source:** `vllm-src/vllm/entrypoints/openai/api_server.py`
 123 | 
 124 | #### `build_app(args, supported_tasks=None)`
 125 | 
 126 | Imported in `areal_vllm_server.py:9` as `_original_build_app`:
 127 | 
 128 | ```python
 129 | from vllm.entrypoints.openai.api_server import build_app as _original_build_app
 130 | ```
 131 | 
 132 | AReaL monkey-patches `build_app` to inject custom routes in
 133 | `areal_vllm_server.py:458-480`:
 134 | 
 135 | ```python
 136 | import vllm.entrypoints.openai.api_server as _api_server_module
 137 | 
 138 | def _areal_build_app(args, supported_tasks=None):
 139 |     app = _original_build_app(args, supported_tasks=supported_tasks)
 140 |     # Remove vLLM's /v1/completions POST route so AReaL's takes precedence
 141 |     app.router.routes = [
 142 |         route for route in app.router.routes
 143 |         if not (hasattr(route, "path") and route.path == "/v1/completions"
 144 |                 and hasattr(route, "methods") and "POST" in route.methods)
 145 |     ]
 146 |     app.include_router(router)
 147 |     return app
 148 | 
 149 | _api_server_module.build_app = _areal_build_app
 150 | ```
 151 | 
 152 | **Check:** Does `build_app` still exist? Still accepts `(args, supported_tasks=None)`?
 153 | Does it return a FastAPI app? Does the returned app still have `router.routes` with
 154 | `path` and `methods` attributes on route objects?
 155 | 
 156 | #### `run_server(args)`
 157 | 
 158 | Imported in `areal_vllm_server.py:10`:
 159 | 
 160 | ```python
 161 | from vllm.entrypoints.openai.api_server import run_server
 162 | ```
 163 | 
 164 | Called in `areal_vllm_server.py:490`:
 165 | 
 166 | ```python
 167 | uvloop.run(run_server(args))
 168 | ```
 169 | 
 170 | **Check:** Signature. Is it still async? Does it still accept parsed args directly? Does
 171 | it internally call `build_app` (which AReaL monkey-patches)?
 172 | 
 173 | ______________________________________________________________________
 174 | 
 175 | ### 2. `vllm.entrypoints.openai.cli_args`
 176 | 
 177 | **Source:** `vllm-src/vllm/entrypoints/openai/cli_args.py`
 178 | 
 179 | #### `make_arg_parser(parser)`
 180 | 
 181 | Called in `areal_vllm_server.py:486`:
 182 | 
 183 | ```python
 184 | parser = make_arg_parser(parser)
 185 | ```
 186 | 
 187 | **Check:** Signature. Does it still accept a parser and return a parser? New required
 188 | args?
 189 | 
 190 | #### `validate_parsed_serve_args(args)`
 191 | 
 192 | Called in `areal_vllm_server.py:488`:
 193 | 
 194 | ```python
 195 | validate_parsed_serve_args(args)
 196 | ```
 197 | 
 198 | **Check:** Signature. Still exists?
 199 | 
 200 | ______________________________________________________________________
 201 | 
 202 | ### 3. `vllm.entrypoints.openai.completion.api_router`
 203 | 
 204 | **Source:** `vllm-src/vllm/entrypoints/openai/completion/api_router.py`
 205 | 
 206 | #### `create_completion` (aliased as `original_create_completion`)
 207 | 
 208 | Imported in `areal_vllm_server.py:12-14`:
 209 | 
 210 | ```python
 211 | from vllm.entrypoints.openai.completion.api_router import (
 212 |     create_completion as original_create_completion,
 213 | )
 214 | ```
 215 | 
 216 | Called in `areal_vllm_server.py:333`:
 217 | 
 218 | ```python
 219 | response = await original_create_completion(request, raw_request)
 220 | ```
 221 | 
 222 | **Check:** Signature `(request: CompletionRequest, raw_request: Request)` still valid?
 223 | Was this function moved or renamed? Is the module path still
 224 | `vllm.entrypoints.openai.completion.api_router`?
 225 | 
 226 | ______________________________________________________________________
 227 | 
 228 | ### 4. `vllm.entrypoints.openai.completion.protocol`
 229 | 
 230 | **Source:** `vllm-src/vllm/entrypoints/openai/completion/protocol.py`
 231 | 
 232 | #### `CompletionRequest`
 233 | 
 234 | Imported in `areal_vllm_server.py:15`:
 235 | 
 236 | ```python
 237 | from vllm.entrypoints.openai.completion.protocol import CompletionRequest
 238 | ```
 239 | 
 240 | Used as type annotation in `areal_vllm_server.py:327`:
 241 | 
 242 | ```python
 243 | async def create_completion(request: CompletionRequest, raw_request: Request):
 244 | ```
 245 | 
 246 | **Check:** Still exists at this module path? Fields unchanged? Was this class moved?
 247 | 
 248 | ______________________________________________________________________
 249 | 
 250 | ### 5. `vllm.entrypoints.openai.engine.protocol`
 251 | 
 252 | **Source:** `vllm-src/vllm/entrypoints/openai/engine/protocol.py`
 253 | 
 254 | #### `ErrorResponse`
 255 | 
 256 | Imported in `areal_vllm_server.py:16`:
 257 | 
 258 | ```python
 259 | from vllm.entrypoints.openai.engine.protocol import ErrorResponse, OpenAIBaseModel
 260 | ```
 261 | 
 262 | Used in route response model in `areal_vllm_server.py:320-322`:
 263 | 
 264 | ```python
 265 | HTTPStatus.BAD_REQUEST.value: {"model": ErrorResponse},
 266 | HTTPStatus.NOT_FOUND.value: {"model": ErrorResponse},
 267 | HTTPStatus.INTERNAL_SERVER_ERROR.value: {"model": ErrorResponse},
 268 | ```
 269 | 
 270 | **Check:** Still exists at this module path?
 271 | 
 272 | #### `OpenAIBaseModel`
 273 | 
 274 | AReaL request classes inherit from it in `areal_vllm_server.py:41-92`:
 275 | 
 276 | ```python
 277 | class UpdateWeightsRequest(OpenAIBaseModel):
 278 |     model_path: str
 279 |     ...
 280 | ```
 281 | 
 282 | **Check:** Still exists? Still a Pydantic model base class? Was it moved?
 283 | 
 284 | ______________________________________________________________________
 285 | 
 286 | ### 6. `vllm.entrypoints.openai.utils`
 287 | 
 288 | **Source:** `vllm-src/vllm/entrypoints/openai/utils.py`
 289 | 
 290 | #### `validate_json_request`
 291 | 
 292 | Imported in `areal_vllm_server.py:17`:
 293 | 
 294 | ```python
 295 | from vllm.entrypoints.openai.utils import validate_json_request
 296 | ```
 297 | 
 298 | Used as a FastAPI dependency in `areal_vllm_server.py:317`:
 299 | 
 300 | ```python
 301 | @router.post("/v1/completions", dependencies=[Depends(validate_json_request)])
 302 | ```
 303 | 
 304 | **Check:** Still exists at this module path? Still usable as a `Depends()` target?
 305 | 
 306 | ______________________________________________________________________
 307 | 
 308 | ### 7. `vllm.entrypoints.utils`
 309 | 
 310 | **Source:** `vllm-src/vllm/entrypoints/utils.py`
 311 | 
 312 | #### `cli_env_setup()`
 313 | 
 314 | Called in `areal_vllm_server.py:482`:
 315 | 
 316 | ```python
 317 | cli_env_setup()
 318 | ```
 319 | 
 320 | **Check:** Signature. Still exists?
 321 | 
 322 | #### `load_aware_call`
 323 | 
 324 | Used as decorator in `areal_vllm_server.py:326`:
 325 | 
 326 | ```python
 327 | @load_aware_call
 328 | async def create_completion(request: CompletionRequest, raw_request: Request):
 329 | ```
 330 | 
 331 | **Check:** Still a decorator? Signature?
 332 | 
 333 | #### `with_cancellation`
 334 | 
 335 | Used as decorator in `areal_vllm_server.py:325`:
 336 | 
 337 | ```python
 338 | @with_cancellation
 339 | @load_aware_call
 340 | async def create_completion(...):
 341 | ```
 342 | 
 343 | **Check:** Still a decorator? Order constraints?
 344 | 
 345 | ______________________________________________________________________
 346 | 
 347 | ### 8. `vllm.logger`
 348 | 
 349 | **Source:** `vllm-src/vllm/logger.py`
 350 | 
 351 | #### `init_logger(name)`
 352 | 
 353 | Called in `areal_vllm_server.py:33` and `vllm_worker_extension.py:15`:
 354 | 
 355 | ```python
 356 | logger = init_logger("areal_vllm_server")
 357 | logger = init_logger("vllm_worker_extension")
 358 | ```
 359 | 
 360 | **Check:** Signature unchanged?
 361 | 
 362 | ______________________________________________________________________
 363 | 
 364 | ### 9. `vllm.utils.argparse_utils`
 365 | 
 366 | **Source:** `vllm-src/vllm/utils/argparse_utils.py`
 367 | 
 368 | #### `FlexibleArgumentParser`
 369 | 
 370 | Used in `areal_vllm_server.py:483`:
 371 | 
 372 | ```python
 373 | parser = FlexibleArgumentParser(
 374 |     description="vLLM OpenAI-Compatible RESTful API server."
 375 | )
 376 | ```
 377 | 
 378 | **Check:** Still exists at this module path? Was it moved (e.g., to `vllm.utils`)?
 379 | 
 380 | ______________________________________________________________________
 381 | 
 382 | ### 10. `vllm.v1.engine` (V1 engine outputs)
 383 | 
 384 | **Source:** `vllm-src/vllm/v1/engine/__init__.py`
 385 | 
 386 | #### `EngineCoreOutput`
 387 | 
 388 | Constructed in `areal_vllm_server.py:355`:
 389 | 
 390 | ```python
 391 | EngineCoreOutput(
 392 |     request_id=req.request_id,
 393 |     new_token_ids=[],
 394 |     finish_reason=FinishReason.ABORT,
 395 |     new_logprobs=None,
 396 |     new_prompt_logprobs_tensors=None,
 397 |     stop_reason=None,
 398 | )
 399 | ```
 400 | 
 401 | **Check:** Constructor fields. New required fields? Field renames? Was
 402 | `new_prompt_logprobs_tensors` renamed? Was `stop_reason` removed?
 403 | 
 404 | #### `EngineCoreOutputs`
 405 | 
 406 | Constructed in `areal_vllm_server.py:371`:
 407 | 
 408 | ```python
 409 | EngineCoreOutputs(outputs=outputs)
 410 | ```
 411 | 
 412 | **Check:** Constructor signature. Still accepts `outputs` list?
 413 | 
 414 | #### `FinishReason`
 415 | 
 416 | Used in `areal_vllm_server.py:358`:
 417 | 
 418 | ```python
 419 | finish_reason=FinishReason.ABORT
 420 | ```
 421 | 
 422 | **Check:** `.ABORT` enum value still exists? Was `FinishReason` moved to a different
 423 | module?
 424 | 
 425 | ______________________________________________________________________
 426 | 
 427 | ### 11. `vllm.v1.engine.core`
 428 | 
 429 | **Source:** `vllm-src/vllm/v1/engine/core.py`
 430 | 
 431 | #### `EngineCore`
 432 | 
 433 | AReaL monkey-patches multiple methods onto this class in `areal_vllm_server.py:421-437`:
 434 | 
 435 | ```python
 436 | setattr(EngineCore, "abort_all_reqs", abort_all_reqs)
 437 | setattr(EngineCore, "areal_injected_update_weight", areal_injected_update_weight)
 438 | setattr(EngineCore, "areal_injected_update_weight_lora", areal_injected_update_weight_lora)
 439 | setattr(EngineCore, "areal_injected_update_weight_xccl", areal_injected_update_weight_xccl)
 440 | setattr(EngineCore, "areal_injected_update_weight_lora_xccl", areal_injected_update_weight_lora_xccl)
 441 | ```
 442 | 
 443 | The patched methods access these EngineCore internals:
 444 | 
 445 | - `self.scheduler` — scheduler object
 446 | - `self.scheduler.running` — set/list of running requests
 447 | - `self.scheduler.waiting` — set/list of waiting requests
 448 | - `self.scheduler.finish_requests(request_ids, RequestStatus.FINISHED_ABORTED)`
 449 | - `self.scheduler.reset_prefix_cache()` — returns bool
 450 | - `self.output_queue.put_nowait((client_index, engine_core_outputs))`
 451 | - `self.collective_rpc(method_name, args=(...))` — calls worker methods
 452 | 
 453 | Request objects in `scheduler.running` / `scheduler.waiting` have:
 454 | 
 455 | - `.request_id`
 456 | - `.client_index`
 457 | 
 458 | **Check:** Does `EngineCore` still have `scheduler`, `output_queue` attributes? Does
 459 | `scheduler` still have `running`, `waiting`, `finish_requests()`, `reset_prefix_cache()`
 460 | methods? Does `EngineCore` still have `collective_rpc()` and `call_utility_async()`? Has
 461 | the scheduler API changed (e.g., different method for aborting requests)? Is there now a
 462 | built-in `abort_all` method that replaces the monkey-patch?
 463 | 
 464 | ______________________________________________________________________
 465 | 
 466 | ### 12. `vllm.v1.engine.output_processor`
 467 | 
 468 | **Source:** `vllm-src/vllm/v1/engine/output_processor.py`
 469 | 
 470 | #### `RequestState`
 471 | 
 472 | Used via TYPE_CHECKING import in `areal_vllm_server.py:30-31`:
 473 | 
 474 | ```python
 475 | if TYPE_CHECKING:
 476 |     from vllm.v1.engine.output_processor import RequestState
 477 | ```
 478 | 
 479 | Used in the `finish_request` monkey-patch at `areal_vllm_server.py:411`:
 480 | 
 481 | ```python
 482 | def finish_request(self, req_state: "RequestState"):
 483 |     if req_state.lora_name is None:
 484 |         return
 485 |     lora_stats = self.lora_name_to_stats[req_state.lora_name]
 486 |     if req_state.request_id in lora_stats.running_requests:
 487 |         lora_stats.running_requests.remove(req_state.request_id)
 488 | ```
 489 | 
 490 | **Check:** Does `RequestState` still have `.lora_name` and `.request_id` attributes? Was
 491 | this class moved? Was it renamed?
 492 | 
 493 | ______________________________________________________________________
 494 | 
 495 | ### 13. `vllm.v1.metrics.stats`
 496 | 
 497 | **Source:** `vllm-src/vllm/v1/metrics/stats.py`
 498 | 
 499 | #### `LoRARequestStates`
 500 | 
 501 | Monkey-patched in `areal_vllm_server.py:444-448`:
 502 | 
 503 | ```python
 504 | setattr(LoRARequestStates, "finish_request", finish_request)
 505 | ```
 506 | 
 507 | This patch is guarded by a version check:
 508 | 
 509 | ```python
 510 | if not pkg_version.is_version_greater_or_equal("vllm", "0.12.0"):
 511 |     setattr(LoRARequestStates, "finish_request", finish_request)
 512 | ```
 513 | 
 514 | **Check:** Does `LoRARequestStates` still exist at this path? Does it still have a
 515 | `finish_request` method? Has the bug (that the monkey-patch fixes) been fixed upstream?
 516 | Does `LoRARequestStates` still have `.lora_name_to_stats` dict with `.running_requests`
 517 | set? If `vllm >= 0.12.0`, is the patch correctly skipped?
 518 | 
 519 | ______________________________________________________________________
 520 | 
 521 | ### 14. `vllm.v1.request`
 522 | 
 523 | **Source:** `vllm-src/vllm/v1/request.py`
 524 | 
 525 | #### `RequestStatus`
 526 | 
 527 | Used in `areal_vllm_server.py:368`:
 528 | 
 529 | ```python
 530 | scheduler.finish_requests(request_ids, RequestStatus.FINISHED_ABORTED)
 531 | ```
 532 | 
 533 | **Check:** `.FINISHED_ABORTED` enum value still exists? Was `RequestStatus` moved?
 534 | 
 535 | ______________________________________________________________________
 536 | 
 537 | ### 15. `vllm.lora.request`
 538 | 
 539 | **Source:** `vllm-src/vllm/lora/request.py`
 540 | 
 541 | #### `LoRARequest`
 542 | 
 543 | Imported in both `areal_vllm_server.py:20` and `vllm_worker_extension.py:8`.
 544 | 
 545 | Constructed in `areal_vllm_server.py:154-161` (attribute-set pattern):
 546 | 
 547 | ```python
 548 | lora_request = LoRARequest(
 549 |     lora_name=lora_name,
 550 |     lora_int_id=lora_int_id,
 551 |     lora_path=runtime_lora_path,
 552 | )
 553 | if base_model_name is not None:
 554 |     lora_request.base_model_name = base_model_name
 555 | ```
 556 | 
 557 | Constructed in `vllm_worker_extension.py:59-64` (constructor arg pattern):
 558 | 
 559 | ```python
 560 | LoRARequest(
 561 |     lora_name=lora_name,
 562 |     lora_int_id=lora_int_id,
 563 |     lora_path=lora_model_path,
 564 |     base_model_name=base_model_name,
 565 | )
 566 | ```
 567 | 
 568 | **Check:** Constructor params. Is `base_model_name` still accepted as constructor arg?
 569 | Is it still settable as an attribute? Renamed fields?
 570 | 
 571 | ______________________________________________________________________
 572 | 
 573 | ### 16. `vllm.lora.lora_model`
 574 | 
 575 | **Source:** `vllm-src/vllm/lora/lora_model.py`
 576 | 
 577 | #### `LoRAModel.from_lora_tensors(...)`
 578 | 
 579 | Called in `vllm_worker_extension.py:235`:
 580 | 
 581 | ```python
 582 | LoRAModel.from_lora_tensors(
 583 |     lora_model_id=self.areal_lora_int_id,
 584 |     tensors=normalized_weights,
 585 |     peft_helper=peft_helper,
 586 |     device=self.model_runner.device,
 587 |     dtype=self.model_runner.lora_manager.lora_config.lora_dtype,
 588 |     model_vocab_size=model_vocab_size,
 589 |     weights_mapper=getattr(self.model_runner.model, "hf_to_vllm_mapper", None),
 590 | )
 591 | ```
 592 | 
 593 | **Check:** `from_lora_tensors` class method still exists? Signature unchanged? New
 594 | required params? `weights_mapper` param still accepted?
 595 | 
 596 | ______________________________________________________________________
 597 | 
 598 | ### 17. `vllm.lora.peft_helper`
 599 | 
 600 | **Source:** `vllm-src/vllm/lora/peft_helper.py`
 601 | 
 602 | #### `PEFTHelper.from_dict(config)`
 603 | 
 604 | Called in `vllm_worker_extension.py:226`:
 605 | 
 606 | ```python
 607 | peft_config = {
 608 |     "r": self.areal_lora_rank,
 609 |     "lora_alpha": self.areal_lora_alpha,
 610 |     "target_modules": self.areal_lora_target_modules,
 611 |     "bias": self.areal_lora_bias,
 612 | }
 613 | peft_helper = PEFTHelper.from_dict(peft_config)
 614 | ```
 615 | 
 616 | **Check:** `from_dict` class method still exists? Expected dict keys unchanged?
 617 | 
 618 | ______________________________________________________________________
 619 | 
 620 | ### 18. `vllm.model_executor.model_loader`
 621 | 
 622 | **Source:** `vllm-src/vllm/model_executor/model_loader/__init__.py`
 623 | 
 624 | #### `get_model_loader(load_config)`
 625 | 
 626 | Called in `vllm_worker_extension.py:32`:
 627 | 
 628 | ```python
 629 | model_loader = get_model_loader(self.model_runner.vllm_config.load_config)
 630 | ```
 631 | 
 632 | Then used as:
 633 | 
 634 | ```python
 635 | model_loader.load_weights(
 636 |     self.model_runner.model, model_config=self.model_runner.model_config
 637 | )
 638 | ```
 639 | 
 640 | **Check:** `get_model_loader` still exists? Return type still has
 641 | `load_weights(model, model_config=...)` method? Was it moved to a different module?
 642 | 
 643 | ______________________________________________________________________
 644 | 
 645 | ### 19. `vllm.envs`
 646 | 
 647 | **Source:** `vllm-src/vllm/envs.py`
 648 | 
 649 | #### `VLLM_USE_V1` (no longer directly checked)
 650 | 
 651 | Previously checked via `if envs.VLLM_USE_V1:` in platform files. AReaL now uses a
 652 | try/except import pattern instead in `cuda.py:31-53` and `unknown.py:31-53`:
 653 | 
 654 | ```python
 655 | @classmethod
 656 | def get_vllm_worker_class(clas):
 657 |     try:
 658 |         from vllm.v1.worker.gpu_worker import Worker
 659 |         return Worker
 660 |     except ImportError:
 661 |         pass
 662 |     try:
 663 |         from vllm.worker.worker import Worker
 664 |         return Worker
 665 |     except ImportError as e:
 666 |         raise RuntimeError("vLLM is not installed or not properly configured.") from e
 667 | ```
 668 | 
 669 | **Check:** Does `vllm.v1.worker.gpu_worker.Worker` still exist? Was V0
 670 | `vllm.worker.worker.Worker` removed entirely? Are there other env vars in `vllm.envs`
 671 | that AReaL might need?
 672 | 
 673 | ______________________________________________________________________
 674 | 
 675 | ### 20. `vllm.v1.worker.gpu_worker` / `vllm.worker.worker`
 676 | 
 677 | **Source:** `vllm-src/vllm/v1/worker/gpu_worker.py` and `vllm-src/vllm/worker/worker.py`
 678 | 
 679 | #### `Worker`
 680 | 
 681 | Imported in `cuda.py` and `unknown.py` for `get_vllm_worker_class()` using try/except
 682 | (see Section 19 above).
 683 | 
 684 | **Check:** `Worker` class still exists at these paths? Was V0 `vllm.worker.worker`
 685 | removed? Was V1 worker moved?
 686 | 
 687 | ______________________________________________________________________
 688 | 
 689 | ### 21. Private/internal APIs used by AReaL
 690 | 
 691 | These are internal vLLM APIs not part of the public interface. They are most likely to
 692 | break on upgrade.
 693 | 
 694 | #### Worker extension model runner internals
 695 | 
 696 | Accessed in `vllm_worker_extension.py`:
 697 | 
 698 | - `self.model_runner.model_config.model` — writable string field (line 31)
 699 | - `self.model_runner.vllm_config.load_config` — VllmConfig load config (line 32)
 700 | - `self.model_runner.model` — the loaded model object (line 35, 144)
 701 | - `self.model_runner.model.load_weights(weights=[(name, tensor)])` — weight loading
 702 |   (line 144)
 703 | - `self.model_runner.device` — torch device (line 136, 200, 239)
 704 | - `self.model_runner.lora_manager` — LoRA manager instance (line 58, 173, 177, 214)
 705 | - `self.model_runner.lora_manager.remove_adapter(lora_int_id)` (line 58, 214)
 706 | - `self.model_runner.lora_manager.list_adapters()` (line 177)
 707 | - `self.model_runner.lora_manager.lora_config.lora_dtype` (line 240)
 708 | - `self.model_runner.lora_manager.lora_config.lora_extra_vocab_size` (line 230)
 709 | - `self.model_runner.lora_manager.vocab_size` (line 233)
 710 | - `self.model_runner.lora_manager._adapter_manager` — private adapter manager (line 185)
 711 | - `self.model_runner.lora_manager._adapter_manager._registered_adapters[id]` — private
 712 |   dict (line 185)
 713 | - `self.model_runner.lora_manager._adapter_manager._add_adapter(model)` — private method
 714 |   (line 247)
 715 | - `self.model_runner.lora_manager._adapter_manager.activate_adapter(id)` — private
 716 |   method (line 248)
 717 | - `self.model_runner.model.hf_to_vllm_mapper` — optional attribute (line 243)
 718 | - `self.model_runner.add_lora(lora_request)` — public method for disk-based LoRA loading
 719 |   (line 66)
 720 | - `self.rank` — worker rank (line 279)
 721 | 
 722 | **Check:** All `model_runner` attributes still exist? Has `lora_manager` been
 723 | restructured? Are `_adapter_manager`, `_registered_adapters`, `_add_adapter`,
 724 | `activate_adapter` still available? Has `load_weights` signature changed on the model
 725 | object? Does `add_lora` still exist on `model_runner`?
 726 | 
 727 | #### EngineCore internals (monkey-patched)
 728 | 
 729 | Accessed by injected methods in `areal_vllm_server.py`:
 730 | 
 731 | - `self.scheduler` — scheduler instance
 732 | - `self.scheduler.running` — iterable of running requests
 733 | - `self.scheduler.waiting` — iterable of waiting requests
 734 | - `self.scheduler.finish_requests(request_ids, status)` — abort method
 735 | - `self.scheduler.reset_prefix_cache()` — returns bool
 736 | - `self.output_queue` — async queue
 737 | - `self.output_queue.put_nowait((client_index, outputs))` — enqueue outputs
 738 | - `self.collective_rpc(method, args=())` — RPC to workers
 739 | - `req.request_id` — on request objects in scheduler queues
 740 | - `req.client_index` — on request objects in scheduler queues
 741 | 
 742 | **Check:** All scheduler attributes/methods still exist? Was `output_queue` renamed or
 743 | restructured? Was `collective_rpc` moved or its signature changed?
 744 | 
 745 | #### Engine client APIs (called from route handlers)
 746 | 
 747 | Accessed via `raw_request.app.state.engine_client` in `areal_vllm_server.py`:
 748 | 
 749 | - `llm.engine_core.call_utility_async(method, *args)` — calls utility method on engine
 750 |   core (lines 173, 188, 202, 214, 298)
 751 | - `llm.collective_rpc(method, args=(...))` — calls method on all workers (lines 233,
 752 |   253, 273)
 753 | 
 754 | **Check:** Does `engine_client` still expose `engine_core` with `call_utility_async()`?
 755 | Does it still expose `collective_rpc()`?
 756 | 
 757 | #### openai_serving_models internals (runtime LoRA registration)
 758 | 
 759 | Accessed in `areal_vllm_server.py:116-166`:
 760 | 
 761 | - `app.state.openai_serving_models` — serving models state object
 762 | - `serving_models.lora_requests` — dict of LoRA requests (name -> LoRARequest)
 763 | - `request.lora_path` — path attribute on LoRARequest
 764 | - `request.lora_int_id` — int id attribute on LoRARequest
 765 | 
 766 | **Check:** Does `app.state.openai_serving_models` still exist? Does it still have a
 767 | `lora_requests` dict? Are the attribute names on LoRARequest objects unchanged?
 768 | 
 769 | ______________________________________________________________________
 770 | 
 771 | ### 22. Environment variables
 772 | 
 773 | Used in `vllm_server.py` and `vllm_remote.py`:
 774 | 
 775 | - `VLLM_CACHE_ROOT` — vLLM compile cache directory
 776 | - `VLLM_ALLOW_RUNTIME_LORA_UPDATING` — set to `"True"` to enable runtime LoRA updates
 777 | 
 778 | **Check:** These env vars still recognized by vLLM? Any renamed? Any new required env
 779 | vars?
 780 | 
 781 | ______________________________________________________________________
 782 | 
 783 | ### 23. vLLM server CLI interface
 784 | 
 785 | AReaL builds vLLM CLI commands in `areal/api/cli_args.py` (`vLLMConfig` dataclass). The
 786 | CLI flags are converted to command-line arguments via `get_py_cmd()`:
 787 | 
 788 | ```python
 789 | vLLMConfig.build_cmd_from_args(args)
 790 | # → python3 -m areal.engine.vllm_ext.areal_vllm_server --model ... --seed ...
 791 | ```
 792 | 
 793 | Fields in `vLLMConfig` that map to vLLM CLI flags:
 794 | 
 795 | - `--model`, `--tokenizer`, `--seed`
 796 | - `--skip-tokenizer-init`, `--enforce-eager`
 797 | - `--dtype`, `--distributed-executor-backend`
 798 | - `--max-num-seqs`, `--block-size`, `--swap-space`
 799 | - `--cpu-offload-gb`, `--disable-sliding-window`
 800 | - `--max-model-len`
 801 | - `--no-enable-chunked-prefill`, `--no-enable-prefix-caching`
 802 | - `--gpu-memory-utilization`
 803 | - `--worker-extension-cls`
 804 | - `--enable-sleep-mode`, `--uvicorn-log-level`
 805 | - `--enable-lora`, `--max-lora-rank`, `--max-loras`, `--lora-modules`
 806 | - `--load-format`, `--trust-remote-code`
 807 | - `--tensor-parallel-size`, `--pipeline-parallel-size`
 808 | - `--host`, `--port`
 809 | 
 810 | **Check:** All CLI flags still accepted? Any renamed (e.g.,
 811 | `--distributed-executor-backend`)? Any removed? New required flags? Has
 812 | `--worker-extension-cls` been renamed or removed? Has `--no-enable-chunked-prefill`
 813 | behavior changed? Does `--enable-sleep-mode` still exist (enables `/sleep` and
 814 | `/wake_up` endpoints)?
 815 | 
 816 | ______________________________________________________________________
 817 | 
 818 | ### 24. vLLM HTTP endpoints
 819 | 
 820 | AReaL interacts with vLLM via HTTP. The following endpoints are used:
 821 | 
 822 | **Standard vLLM endpoints:**
 823 | 
 824 | - `GET /health` — health check (`vllm_remote.py:221`)
 825 | - `GET /v1/models` — server readiness check (`vllm_server.py:72`)
 826 | - `POST /v1/completions` — text generation (`vllm_remote.py:90`,
 827 |   `areal_vllm_server.py:316`)
 828 | - `POST /v1/chat/completions` — VLM chat generation (`vllm_remote.py:87`)
 829 | - `POST /v1/load_lora_adapter` — load LoRA adapter from disk (`vllm_remote.py:131`)
 830 | - `POST /sleep` — offload model to CPU (`vllm_remote.py:229`)
 831 | - `POST /wake_up` — reload model from CPU, with optional `?tags=` query
 832 |   (`vllm_remote.py:248`)
 833 | 
 834 | **Custom AReaL endpoints** (registered via `@router.post` in `areal_vllm_server.py`):
 835 | 
 836 | - `POST /areal_update_weights` — update full model weights from disk
 837 | - `POST /areal_update_weights_lora` — update LoRA weights from disk
 838 | - `POST /areal_update_weights_xccl` — update full model weights via NCCL/HCCL
 839 | - `POST /areal_update_weights_lora_xccl` — update LoRA weights via NCCL/HCCL
 840 | - `POST /areal_init_weights_update_group` — initialize distributed weight update group
 841 | - `POST /areal_set_update_weight_meta` — set weight metadata for XCCL update
 842 | - `POST /areal_set_update_weight_meta_lora` — set LoRA weight metadata for XCCL update
 843 | - `POST /areal_pause_generation` — pause generation and abort all requests
 844 | - `POST /areal_continue_generation` — resume generation
 845 | 
 846 | **Check:** Standard endpoints still at same paths? Response format unchanged? `/sleep`
 847 | and `/wake_up` still exist? `/v1/completions` response still has
 848 | `choices[0].logprobs.tokens` or `choices[0].logprobs.content` format? Has
 849 | `return_tokens_as_token_ids` param changed behavior (token format `"token:123"`)?
 850 | 
 851 | ______________________________________________________________________
 852 | 
 853 | ## Version-Guarded Code
 854 | 
 855 | AReaL has version-specific code paths:
 856 | 
 857 | ```python
 858 | # areal_vllm_server.py:439-448
 859 | # Patch for LoRARequestStates management in vllm < v0.11.0
 860 | # This may be removed with vllm >= 0.12.x
 861 | from areal.utils import pkg_version
 862 | 
 863 | if not pkg_version.is_version_greater_or_equal("vllm", "0.12.0"):
 864 |     setattr(LoRARequestStates, "finish_request", finish_request)
 865 | ```
 866 | 
 867 | **Check:** If upgrading to >= 0.12.0, verify the upstream
 868 | `LoRARequestStates.finish_request` fix is present. If upgrading past the fix version,
 869 | the guarded code becomes dead code — note for cleanup.
 870 | 
 871 | Also in `areal/api/cli_args.py` (comments):
 872 | 
 873 | ```python
 874 | # IMPORTANT: vLLM V1 engine forces enable_chunked_prefill=True by default
 875 | # TODO(vllm-v0.11.0): vLLM v0.11.0 has inference quality issues when
 876 | # temperature=1.0
 877 | ```
 878 | 
 879 | **Check:** Have these known issues been fixed in the target version?
 880 | 
 881 | ______________________________________________________________________
 882 | 
 883 | ## Upgrade Workflow
 884 | 
 885 | ### Step 0: Prepare vLLM source
 886 | 
 887 | Clone or checkout the target version as described in Prerequisites above.
 888 | 
 889 | ### Step 1: Audit `vllm` API signatures
 890 | 
 891 | For EACH entry in the API Usage Catalog above:
 892 | 
 893 | 1. Open the upstream source file at the target version.
 894 | 1. Compare the function/class signature against the current AReaL invocation.
 895 | 1. Flag any of:
 896 |    - **Removed parameters** still passed by AReaL → must remove from call site
 897 |    - **Renamed parameters** → must rename in call site
 898 |    - **New required parameters** (no default) → must add to call site
 899 |    - **New optional parameters** with useful defaults → document but skip
 900 |    - **Changed return types** → must update consumers
 901 |    - **Removed functions/classes** → must find replacement
 902 |    - **Moved modules** → must update import paths
 903 |    - **Changed method signatures** on returned/internal objects → must update call sites
 904 | 1. Record findings per-file.
 905 | 
 906 | ### Step 2: Audit private/internal API compatibility
 907 | 
 908 | vLLM's internal APIs (Section 21) are the most fragile. For each:
 909 | 
 910 | 1. Search the upstream source for the accessed attribute/method.
 911 | 1. Verify it still exists at the expected path.
 912 | 1. Check if vLLM has added official APIs that replace the private access patterns.
 913 | 1. If an official API exists, prefer migrating to it over maintaining private API
 914 |    access.
 915 | 
 916 | ### Step 3: Audit vLLM CLI flag compatibility
 917 | 
 918 | Compare `vLLMConfig` fields in `areal/api/cli_args.py` against the vLLM CLI:
 919 | 
 920 | ```bash
 921 | cd vllm-src && python -m vllm.entrypoints.openai.api_server --help
 922 | ```
 923 | 
 924 | Flag any removed/renamed CLI arguments.
 925 | 
 926 | ### Step 4: Update `pyproject.toml`
 927 | 
 928 | Update the `vllm` version pin in `pyproject.toml`:
 929 | 
 930 | ```toml
 931 | vllm = [
 932 | "vllm==X.Y.Z; sys_platform == 'linux' and platform_machine == 'x86_64'",
 933 | ]
 934 | ```
 935 | 
 936 | Run `uv lock` to verify dependency resolution.
 937 | 
 938 | ### Step 5: Apply code changes
 939 | 
 940 | For each flagged incompatibility from Steps 1-3:
 941 | 
 942 | 1. Update the call site in the affected file.
 943 | 1. Preserve existing behavior — do NOT refactor beyond what's required.
 944 | 1. If a function was removed, check the upstream migration guide or changelog.
 945 | 1. If a module was moved, update the import path.
 946 | 
 947 | Priority order for applying changes:
 948 | 
 949 | 1. `areal/engine/vllm_ext/areal_vllm_server.py` (highest risk — monkey-patches, V1
 950 |    engine internals, many imports)
 951 | 1. `areal/engine/vllm_ext/vllm_worker_extension.py` (private API consumer — model
 952 |    runner, LoRA manager)
 953 | 1. `areal/engine/vllm_remote.py` (HTTP interface — response parsing, endpoint paths)
 954 | 1. `areal/infra/platforms/cuda.py` (V0/V1 worker import)
 955 | 1. `areal/infra/platforms/unknown.py` (same as cuda.py)
 956 | 1. `areal/infra/launcher/vllm_server.py` (env vars, server lifecycle)
 957 | 1. `areal/api/cli_args.py` (`vLLMConfig` — CLI flag mapping)
 958 | 1. `areal/infra/launcher/ray.py`
 959 | 1. `areal/infra/launcher/local.py`
 960 | 1. `areal/infra/launcher/slurm.py`
 961 | 1. `areal/trainer/rl_trainer.py`
 962 | 1. Test files
 963 | 
 964 | ### Step 6: Update version-guarded code
 965 | 
 966 | 1. Review the `pkg_version.is_version_greater_or_equal("vllm", "0.12.0")` guard in
 967 |    `areal_vllm_server.py`. If upgrading to >= 0.12.0, verify the upstream fix and
 968 |    potentially remove the dead code path.
 969 | 1. Review TODO comments referencing specific vLLM versions.
 970 | 
 971 | ### Step 7: Run pre-commit and tests
 972 | 
 973 | ```bash
 974 | pre-commit run --all-files
 975 | uv run pytest tests/test_inference_engines.py -v
 976 | uv run pytest tests/test_model_utils.py -v
 977 | uv run pytest tests/test_allocation_mode.py -v
 978 | ```
 979 | 
 980 | If a GPU with vLLM installed is available:
 981 | 
 982 | ```bash
 983 | uv run pytest tests/test_examples.py -v -k vllm
 984 | ```
 985 | 
 986 | ### Step 8: Report changes
 987 | 
 988 | Output a summary in this format:
 989 | 
 990 | ```
 991 | ## Upgrade Summary: vLLM ${OLD_VERSION} → ${NEW_VERSION}
 992 | 
 993 | ### Breaking Changes Found
 994 | - [file:line] description of change needed
 995 | 
 996 | ### Module Moves / Renames
 997 | - [old_path] → [new_path] (affects: list of AReaL files)
 998 | 
 999 | ### Private API Changes
1000 | - [internal_api] description of change (affects: list of AReaL files)
1001 | 
1002 | ### CLI Flag Changes
1003 | - [flag] description (affects: vLLMConfig in cli_args.py)
1004 | 
1005 | ### API Additions (new optional params, informational)
1006 | - [upstream_file] description
1007 | 
1008 | ### Files Modified
1009 | - path/to/file.py: description of change
1010 | 
1011 | ### Version-Guarded Code
1012 | - [file:line] status of version guard (still needed / can be removed)
1013 | 
1014 | ### Tests
1015 | - ✅ pre-commit passed
1016 | - ✅ test_inference_engines passed
1017 | - ✅ test_model_utils passed
1018 | - ✅ test_allocation_mode passed
1019 | - ⬚ integration tests (requires GPU with vLLM installed)
1020 | ```
1021 | 
1022 | If there are unresolvable breaking changes, STOP and ask the user before proceeding.
```


---
## .claude/commands/create-pr.md

```
   1 | ---
   2 | name: create-pr
   3 | description: Rebase from the latest `origin/main`, squash the commits from it, and then create a PR on github with intelligent commit messages based on staged changes. Invoke with /create-pr.
   4 | ---
   5 | 
   6 | # Create Pull Request
   7 | 
   8 | Rebase from the latest `origin/main`, squash commits, and create a PR on GitHub with an
   9 | intelligent title and description.
  10 | 
  11 | ## Usage
  12 | 
  13 | ```
  14 | /create-pr [--draft] [--base <branch>]
  15 | ```
  16 | 
  17 | **Arguments:**
  18 | 
  19 | - `--draft`: Create as draft PR
  20 | - `--base <branch>`: Target branch (default: `main`)
  21 | 
  22 | ## Workflow
  23 | 
  24 | ### Step 1: Verify Prerequisites
  25 | 
  26 | ```bash
  27 | # Check current branch
  28 | git branch --show-current
  29 | 
  30 | # Check if on main/master (should NOT be)
  31 | if [[ $(git branch --show-current) == "main" || $(git branch --show-current) == "master" ]]; then
  32 |   echo "ERROR: Cannot create PR from main/master branch"
  33 |   exit 1
  34 | fi
  35 | 
  36 | # Check for uncommitted changes
  37 | git status --short
  38 | 
  39 | # Ensure gh CLI is available
  40 | gh --version
  41 | ```
  42 | 
  43 | **Action:** If there are uncommitted changes, stop, and then ask user to commit or stash
  44 | them first.
  45 | 
  46 | ### Step 1.5: Determine Push Remote (Fork Support)
  47 | 
  48 | Check if user has push access to `origin`, and if not, identify the fork remote.
  49 | 
  50 | ```bash
  51 | # List all remotes
  52 | git remote -v
  53 | 
  54 | # Try to determine push remote
  55 | # Option 1: Check if origin is writable (try a dry-run push)
  56 | git push --dry-run origin $(git branch --show-current) 2>&1
  57 | 
  58 | # Option 2: Check gh auth status and repo permissions
  59 | gh auth status
  60 | gh repo view --json owner,name,viewerPermission
  61 | ```
  62 | 
  63 | **Logic for Determining Push Remote:**
  64 | 
  65 | **If `origin` is writable**: Use `origin` directly (maintainer workflow)
  66 | 
  67 | **If `origin` is NOT writable**: Look for a fork remote
  68 | 
  69 | - Common fork remote names: `fork`, `user`, `<username>`, or any remote pointing to
  70 |   user's fork
  71 | - Verify the fork remote points to user's own fork via
  72 |   `gh repo view <remote-url> --json owner`
  73 | 
  74 | **If no fork remote found**: Ask user to add their fork as a remote:
  75 | 
  76 | ```bash
  77 | git remote add fork https://github.com/<username>/AReaL.git
  78 | ```
  79 | 
  80 | **Store for later use:**
  81 | 
  82 | - `PUSH_REMOTE`: The remote to push to (e.g., `origin` or `fork`)
  83 | - `UPSTREAM_REPO`: The upstream repo for PR target (e.g., `inclusionAI/AReaL`)
  84 | - `FORK_OWNER`: Fork owner username (for `--head` parameter if needed)
  85 | 
  86 | ```bash
  87 | # Example detection script
  88 | UPSTREAM_REPO="inclusionAI/AReaL"
  89 | PUSH_REMOTE=""
  90 | 
  91 | # Check if we can push to origin
  92 | if git push --dry-run origin HEAD 2>/dev/null; then
  93 |   PUSH_REMOTE="origin"
  94 | else
  95 |   # Find fork remote (any remote that's not origin and points to user's fork)
  96 |   for remote in $(git remote); do
  97 |     if [[ "$remote" != "origin" ]]; then
  98 |       remote_url=$(git remote get-url "$remote" 2>/dev/null)
  99 |       if [[ "$remote_url" =~ github\.com/([^/]+)/AReaL ]]; then
 100 |         PUSH_REMOTE="$remote"
 101 |         FORK_OWNER="${BASH_REMATCH[1]}"
 102 |         break
 103 |       fi
 104 |     fi
 105 |   done
 106 | fi
 107 | 
 108 | if [[ -z "$PUSH_REMOTE" ]]; then
 109 |   echo "ERROR: No writable remote found. Please add your fork:"
 110 |   echo "  git remote add fork https://github.com/<username>/AReaL.git"
 111 |   exit 1
 112 | fi
 113 | ```
 114 | 
 115 | ### Step 2: Check for Existing PR
 116 | 
 117 | ```bash
 118 | # Check if PR already exists for current branch
 119 | gh pr view --json number,title,url 2>/dev/null || echo "No existing PR"
 120 | ```
 121 | 
 122 | **Handle Existing PR:**
 123 | 
 124 | - If PR exists, inform user and ask permission to force-update it
 125 | - Warn that this will rewrite the commit history and PR description
 126 | - If user declines, abort the process
 127 | 
 128 | ### Step 3: Fetch and Rebase
 129 | 
 130 | ```bash
 131 | # Fetch latest from origin
 132 | git fetch origin main
 133 | 
 134 | # Check divergence
 135 | git log --oneline HEAD ^origin/main
 136 | 
 137 | # Non-interactive rebase onto origin/main
 138 | git rebase origin/main
 139 | ```
 140 | 
 141 | **Handle Conflicts:** If rebase fails due to conflicts, abort and let user handle rebase
 142 | manually:
 143 | 
 144 | ```bash
 145 | # On rebase failure, abort automatically
 146 | git rebase --abort
 147 | 
 148 | # Inform user to resolve conflicts manually
 149 | echo "Rebase failed due to conflicts. Please resolve manually and retry /create-pr"
 150 | exit 1
 151 | ```
 152 | 
 153 | ### Step 4: Squash Commits into Single Commit
 154 | 
 155 | After successful rebase, squash all commits since `origin/main` into a single commit:
 156 | 
 157 | ```bash
 158 | # Count commits to squash
 159 | git rev-list --count origin/main..HEAD
 160 | 
 161 | # Soft reset to origin/main (keeps changes staged)
 162 | git reset --soft origin/main
 163 | 
 164 | # Generate commit message using commit-conventions skill
 165 | # See .claude/skills/commit-conventions/SKILL.md for format rules
 166 | ```
 167 | 
 168 | **Generate Commit Message** (following `commit-conventions` skill):
 169 | 
 170 | 1. Analyze staged changes:
 171 | 
 172 |    ```bash
 173 |    git diff --cached --name-only
 174 |    git diff --cached
 175 |    ```
 176 | 
 177 | 1. Categorize changes (feat/fix/docs/refactor/test/chore/perf)
 178 | 
 179 | 1. Determine scope from changed files (workflow/engine/reward/dataset/api/docs/etc.)
 180 | 
 181 | 1. Generate message in format:
 182 | 
 183 |    ```
 184 |    <type>(<scope>): <subject>
 185 | 
 186 |    <body>
 187 | 
 188 |    [Optional sections:]
 189 |    Key changes:
 190 |    - change 1
 191 |    - change 2
 192 | 
 193 |    Refs: #123, #456
 194 |    ```
 195 | 
 196 | 1. Commit with generated message:
 197 | 
 198 |    ```bash
 199 |    git commit -m "$(cat <<'EOF'
 200 |    <generated commit message>
 201 |    EOF
 202 |    )"
 203 |    ```
 204 | 
 205 | ### Step 5: Analyze Combined Changes
 206 | 
 207 | After squashing into a single commit:
 208 | 
 209 | ```bash
 210 | # Get all changes since origin/main
 211 | git diff origin/main...HEAD --name-only
 212 | 
 213 | # Get full diff content
 214 | git diff origin/main...HEAD
 215 | 
 216 | # Check commit history
 217 | git log --oneline origin/main..HEAD
 218 | ```
 219 | 
 220 | **Categorize Changes:**
 221 | 
 222 | Follow same categorization as the `commit-conventions` skill:
 223 | 
 224 | | Type       | When to Use                     |
 225 | | ---------- | ------------------------------- |
 226 | | `feat`     | New feature or capability       |
 227 | | `fix`      | Bug fix                         |
 228 | | `docs`     | Documentation only              |
 229 | | `refactor` | Code change without feature/fix |
 230 | | `test`     | Adding or fixing tests          |
 231 | | `chore`    | Build, deps, config changes     |
 232 | | `perf`     | Performance improvement         |
 233 | 
 234 | **Determine Scope:**
 235 | 
 236 | Infer from changed files:
 237 | 
 238 | - `areal/workflow/` → `workflow`
 239 | - `areal/engine/` → `engine`
 240 | - `areal/reward/` → `reward`
 241 | - `areal/dataset/` → `dataset`
 242 | - `areal/api/` → `api`
 243 | - `areal/utils/` → `utils`
 244 | - `areal/infra/` → `infra`
 245 | - `docs/` → `docs`
 246 | - `examples/` → `examples`
 247 | - Multiple areas → omit scope or use broader term
 248 | 
 249 | ### Step 6: Generate PR Title and Description
 250 | 
 251 | **PR Title Format:**
 252 | 
 253 | ```
 254 | <type>(<scope>): <brief description>
 255 | ```
 256 | 
 257 | **Rules:**
 258 | 
 259 | - Keep under 70 characters
 260 | - Use imperative mood
 261 | - No period at end
 262 | - Mirror commit message style
 263 | 
 264 | **PR Description Format:**
 265 | 
 266 | MUST strictly follow the [GitHub PR template](../../.github/PULL_REQUEST_TEMPLATE.md):
 267 | 
 268 | ```markdown
 269 | ## Description
 270 | 
 271 | <!-- Clear and concise description of what this PR does -->
 272 | 
 273 | ## Related Issue
 274 | 
 275 | <!-- Link to the issue this PR addresses -->
 276 | Fixes #(issue)
 277 | 
 278 | ## Type of Change
 279 | 
 280 | <!-- Mark the relevant option with an 'x' -->
 281 | 
 282 | - [ ] Bug fix (non-breaking change that fixes an issue)
 283 | - [ ] New feature (non-breaking change that adds functionality)
 284 | - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
 285 | - [ ] Documentation update
 286 | - [ ] Code refactoring (no functional changes)
 287 | - [ ] Performance improvement
 288 | - [ ] Test coverage improvement
 289 | 
 290 | ## Checklist
 291 | 
 292 | <!-- Mark with 'x' what you've done -->
 293 | 
 294 | - [ ] I have read the [Contributing Guide](../CONTRIBUTING.md)
 295 | - [ ] I have run formatting tools (pre-commit or manual)
 296 | - [ ] I have run relevant unit tests and they pass
 297 | - [ ] I have added tests for new functionality
 298 | - [ ] I have updated documentation if needed
 299 | - [ ] My branch is up to date with main
 300 | - [ ] This PR introduces breaking changes (if yes, fill out details below)
 301 | - [ ] If this PR changes documentation, I have built and previewed it locally with `jb build docs`
 302 | - [ ] No critical issues raised by AI reviewers (`/gemini review`)
 303 | 
 304 | **Breaking Change Details (if applicable):**
 305 | 
 306 | <!-- Describe what breaks and how users should migrate -->
 307 | 
 308 | ## Additional Context
 309 | 
 310 | <!-- Add any other context, screenshots, logs, or explanations here -->
 311 | ```
 312 | 
 313 | **How to Fill the Template:**
 314 | 
 315 | 1. **Description**: 2-4 sentences explaining what this PR does and why
 316 | 1. **Related Issue**: Link to issue (search for related issues if exists)
 317 | 1. **Type of Change**: Mark ONE primary type with `[x]`
 318 | 1. **Checklist**: Mark completed items with `[x]`, leave uncompleted as `[ ]`
 319 | 1. **Breaking Change Details**: Only if breaking changes checkbox is marked
 320 | 1. **Additional Context**: Any extra info, related PRs, performance numbers, etc.
 321 | 
 322 | ### Step 7: Push and Create/Update PR
 323 | 
 324 | Show preview to user:
 325 | 
 326 | ```
 327 | ─────────────────────────────────────────────────
 328 | Remote: <fork-remote> (fork) → origin (upstream)
 329 | Branch: feat/vision-rlvr → main
 330 | 
 331 | PR Title:
 332 | feat(workflow): add vision support to RLVR
 333 | 
 334 | PR Description:
 335 | ## Description
 336 | 
 337 | Add VisionRLVRWorkflow for vision-language RL training. Supports image inputs
 338 | alongside text prompts and integrates with existing RLVR pipeline.
 339 | 
 340 | ## Related Issue
 341 | 
 342 | Fixes #789
 343 | 
 344 | ## Type of Change
 345 | 
 346 | - [ ] Bug fix (non-breaking change that fixes an issue)
 347 | - [x] New feature (non-breaking change that adds functionality)
 348 | - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
 349 | - [ ] Documentation update
 350 | - [ ] Code refactoring (no functional changes)
 351 | - [ ] Performance improvement
 352 | - [ ] Test coverage improvement
 353 | 
 354 | ## Checklist
 355 | 
 356 | - [x] I have read the [Contributing Guide](../CONTRIBUTING.md)
 357 | - [x] I have run formatting tools (pre-commit or manual)
 358 | - [ ] I have run relevant unit tests and they pass
 359 | - [x] I have added tests for new functionality
 360 | - [x] I have updated documentation if needed
 361 | - [x] My branch is up to date with main
 362 | - [ ] This PR introduces breaking changes (if yes, fill out details below)
 363 | - [x] If this PR changes documentation, I have built and previewed it locally with `jb build docs`
 364 | - [ ] No critical issues raised by AI reviewers (`/gemini review`)
 365 | 
 366 | **Breaking Change Details (if applicable):**
 367 | 
 368 | N/A
 369 | 
 370 | ## Additional Context
 371 | 
 372 | Requires Pillow>=10.0.0 for image processing.
 373 | 
 374 | Files changed:
 375 | - `areal/workflow/vision_rlvr.py`: New VisionRLVRWorkflow class
 376 | - `areal/api/workflow_api.py:45`: Add vision config fields
 377 | - `examples/vision_rlvr.py`: Example training script
 378 | - `docs/workflows/vision.md`: Documentation
 379 | 
 380 | ─────────────────────────────────────────────────
 381 | 
 382 | Commands to execute:
 383 | 1. git push -f -u <fork-remote> feat/vision-rlvr
 384 | 2. gh pr create --repo inclusionAI/AReaL --head <username>:feat/vision-rlvr --base main --title "..." --body "..." [--draft]
 385 | ─────────────────────────────────────────────────
 386 | ```
 387 | 
 388 | **Confirm with user**, then execute:
 389 | 
 390 | ```bash
 391 | # Get current branch name
 392 | CURRENT_BRANCH=$(git branch --show-current)
 393 | 
 394 | # Force push branch to determined remote (required after squash)
 395 | # PUSH_REMOTE was determined in Step 1.5
 396 | git push -f -u "$PUSH_REMOTE" "$CURRENT_BRANCH"
 397 | 
 398 | # Determine if this is a fork PR (cross-repo)
 399 | if [[ "$PUSH_REMOTE" != "origin" ]]; then
 400 |   # Fork workflow: PR from fork to upstream
 401 |   PR_HEAD="${FORK_OWNER}:${CURRENT_BRANCH}"
 402 |   GH_PR_REPO="--repo ${UPSTREAM_REPO}"
 403 | else
 404 |   # Maintainer workflow: PR within same repo
 405 |   PR_HEAD="$CURRENT_BRANCH"
 406 |   GH_PR_REPO=""
 407 | fi
 408 | 
 409 | # Create or edit PR using gh CLI with GitHub template format
 410 | # If PR exists, use 'gh pr edit' instead of 'gh pr create'
 411 | if gh pr view --repo "${UPSTREAM_REPO}" --head "${PR_HEAD}" &>/dev/null; then
 412 |   # Update existing PR
 413 |   gh pr edit \
 414 |     --repo "${UPSTREAM_REPO}" \
 415 |     --title "feat(workflow): add vision support to RLVR" \
 416 |     --body "$(cat <<'EOF'
 417 | [PR description here]
 418 | EOF
 419 | )"
 420 | else
 421 |   # Create new PR
 422 |   gh pr create \
 423 |     --repo "${UPSTREAM_REPO}" \
 424 |     --head "${PR_HEAD}" \
 425 |     --base main \
 426 |     --title "feat(workflow): add vision support to RLVR" \
 427 |     --body "$(cat <<'EOF'
 428 | ## Description
 429 | 
 430 | Add VisionRLVRWorkflow for vision-language RL training. Supports image inputs
 431 | alongside text prompts and integrates with existing RLVR pipeline.
 432 | 
 433 | ## Related Issue
 434 | 
 435 | Fixes #789
 436 | 
 437 | ## Type of Change
 438 | 
 439 | - [ ] Bug fix (non-breaking change that fixes an issue)
 440 | - [x] New feature (non-breaking change that adds functionality)
 441 | - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
 442 | - [ ] Documentation update
 443 | - [ ] Code refactoring (no functional changes)
 444 | - [ ] Performance improvement
 445 | - [ ] Test coverage improvement
 446 | 
 447 | ## Checklist
 448 | 
 449 | - [x] I have read the [Contributing Guide](../CONTRIBUTING.md)
 450 | - [x] I have run formatting tools (pre-commit or manual)
 451 | - [ ] I have run relevant unit tests and they pass
 452 | - [x] I have added tests for new functionality
 453 | - [x] I have updated documentation if needed
 454 | - [x] My branch is up to date with main
 455 | - [ ] This PR introduces breaking changes (if yes, fill out details below)
 456 | - [x] If this PR changes documentation, I have built and previewed it locally with `jb build docs`
 457 | - [ ] No critical issues raised by AI reviewers (`/gemini review`)
 458 | 
 459 | **Breaking Change Details (if applicable):**
 460 | 
 461 | N/A
 462 | 
 463 | ## Additional Context
 464 | 
 465 | Requires Pillow>=10.0.0 for image processing.
 466 | 
 467 | Files changed:
 468 | - `areal/workflow/vision_rlvr.py`: New VisionRLVRWorkflow class
 469 | - `areal/api/workflow_api.py:45`: Add vision config fields
 470 | - `examples/vision_rlvr.py`: Example training script
 471 | - `docs/workflows/vision.md`: Documentation
 472 | EOF
 473 | )"
 474 | fi
 475 | ```
 476 | 
 477 | Add `--draft` flag if requested.
 478 | 
 479 | **Capture PR URL** and display to user:
 480 | 
 481 | ```
 482 | ✓ PR created/updated successfully!
 483 | https://github.com/inclusionAI/AReaL/pull/123
 484 | ```
 485 | 
 486 | ## Examples
 487 | 
 488 | ### Example 1: Feature PR
 489 | 
 490 | **Changes:** New dataset loader for MATH dataset
 491 | 
 492 | **PR Title:**
 493 | 
 494 | ```
 495 | feat(dataset): add MATH dataset loader
 496 | ```
 497 | 
 498 | **PR Description:**
 499 | 
 500 | ```markdown
 501 | ## Description
 502 | 
 503 | Add MATHDataset loader for mathematics problem solving with LaTeX rendering and
 504 | symbolic math parsing. Includes reward function for automatic answer verification
 505 | and full test coverage.
 506 | 
 507 | ## Related Issue
 508 | 
 509 | Fixes #456
 510 | 
 511 | ## Type of Change
 512 | 
 513 | - [ ] Bug fix (non-breaking change that fixes an issue)
 514 | - [x] New feature (non-breaking change that adds functionality)
 515 | - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
 516 | - [ ] Documentation update
 517 | - [ ] Code refactoring (no functional changes)
 518 | - [ ] Performance improvement
 519 | - [ ] Test coverage improvement
 520 | 
 521 | ## Checklist
 522 | 
 523 | - [x] I have read the [Contributing Guide](../CONTRIBUTING.md)
 524 | - [x] I have run formatting tools (pre-commit or manual)
 525 | - [x] I have run relevant unit tests and they pass
 526 | - [x] I have added tests for new functionality
 527 | - [x] I have updated documentation if needed
 528 | - [x] My branch is up to date with main
 529 | - [ ] This PR introduces breaking changes (if yes, fill out details below)
 530 | - [x] If this PR changes documentation, I have built and previewed it locally with `jb build docs`
 531 | - [ ] No critical issues raised by AI reviewers (`/gemini review`)
 532 | 
 533 | **Breaking Change Details (if applicable):**
 534 | 
 535 | N/A
 536 | 
 537 | ## Additional Context
 538 | 
 539 | Dataset requires ~500MB download on first use. Added comprehensive test suite
 540 | covering all 12,500 problems with >95% reward function accuracy.
 541 | 
 542 | Files changed:
 543 | - `areal/dataset/math.py`: New MATHDataset class
 544 | - `areal/reward/math_reward.py`: Symbolic math reward function
 545 | - `examples/math_training.py`: Training script
 546 | - `docs/datasets/math.md`: Dataset documentation
 547 | - `tests/test_math_dataset.py`: Unit tests
 548 | ```
 549 | 
 550 | ### Example 2: Bug Fix PR
 551 | 
 552 | **Changes:** Fix memory leak in ArchonEngine
 553 | 
 554 | **PR Title:**
 555 | 
 556 | ```
 557 | fix(engine): resolve memory leak in ArchonEngine rollout
 558 | ```
 559 | 
 560 | **PR Description:**
 561 | 
 562 | ```markdown
 563 | ## Description
 564 | 
 565 | Fix memory leak during ArchonEngine rollout phase by clearing cached activations
 566 | after each batch and moving tensors to CPU before deletion. Reduces memory usage
 567 | by ~2GB per rollout iteration.
 568 | 
 569 | ## Related Issue
 570 | 
 571 | Fixes #872
 572 | 
 573 | ## Type of Change
 574 | 
 575 | - [x] Bug fix (non-breaking change that fixes an issue)
 576 | - [ ] New feature (non-breaking change that adds functionality)
 577 | - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
 578 | - [ ] Documentation update
 579 | - [ ] Code refactoring (no functional changes)
 580 | - [ ] Performance improvement
 581 | - [ ] Test coverage improvement
 582 | 
 583 | ## Checklist
 584 | 
 585 | - [x] I have read the [Contributing Guide](../CONTRIBUTING.md)
 586 | - [x] I have run formatting tools (pre-commit or manual)
 587 | - [x] I have run relevant unit tests and they pass
 588 | - [x] I have added tests for new functionality
 589 | - [ ] I have updated documentation if needed
 590 | - [x] My branch is up to date with main
 591 | - [ ] This PR introduces breaking changes (if yes, fill out details below)
 592 | - [ ] If this PR changes documentation, I have built and previewed it locally with `jb build docs`
 593 | - [ ] No critical issues raised by AI reviewers (`/gemini review`)
 594 | 
 595 | **Breaking Change Details (if applicable):**
 596 | 
 597 | N/A
 598 | 
 599 | ## Additional Context
 600 | 
 601 | Tested with 100 rollout iterations without OOM. Memory usage stable at 8GB
 602 | (previously would grow to 10GB+). Output correctness validated unchanged.
 603 | 
 604 | Backported to v0.5.x branch.
 605 | 
 606 | Files changed:
 607 | - `areal/engine/archon.py:234`: Add explicit cache clearing
 608 | - `areal/engine/archon.py:456`: Move tensor to CPU before deletion
 609 | - `tests/test_archon_memory.py`: Add memory leak regression test
 610 | ```
 611 | 
 612 | ### Example 3: Breaking Change PR
 613 | 
 614 | **Changes:** Refactor reward API for better extensibility
 615 | 
 616 | **PR Title:**
 617 | 
 618 | ```
 619 | refactor(reward): simplify reward function interface
 620 | ```
 621 | 
 622 | **PR Description:**
 623 | 
 624 | ```markdown
 625 | ## Description
 626 | 
 627 | Simplify reward function API from 4 methods to 2 by consolidating compute and
 628 | compute_batch into a single batched interface. Improves type hints and
 629 | documentation. All existing reward functions updated.
 630 | 
 631 | ## Related Issue
 632 | 
 633 | Fixes #901
 634 | 
 635 | ## Type of Change
 636 | 
 637 | - [ ] Bug fix (non-breaking change that fixes an issue)
 638 | - [ ] New feature (non-breaking change that adds functionality)
 639 | - [x] Breaking change (fix or feature that would cause existing functionality to not work as expected)
 640 | - [ ] Documentation update
 641 | - [ ] Code refactoring (no functional changes)
 642 | - [ ] Performance improvement
 643 | - [ ] Test coverage improvement
 644 | 
 645 | ## Checklist
 646 | 
 647 | - [x] I have read the [Contributing Guide](../CONTRIBUTING.md)
 648 | - [x] I have run formatting tools (pre-commit or manual)
 649 | - [x] I have run relevant unit tests and they pass
 650 | - [ ] I have added tests for new functionality
 651 | - [x] I have updated documentation if needed
 652 | - [x] My branch is up to date with main
 653 | - [x] This PR introduces breaking changes (if yes, fill out details below)
 654 | - [x] If this PR changes documentation, I have built and previewed it locally with `jb build docs`
 655 | - [ ] No critical issues raised by AI reviewers (`/gemini review`)
 656 | 
 657 | **Breaking Change Details (if applicable):**
 658 | 
 659 | Old `compute_batch` method is deprecated and will be removed in v0.7.0.
 660 | 
 661 | See migration guide in `docs/migration/reward_api.md` for details.
 662 | 
 663 | ## Additional Context
 664 | 
 665 | All existing tests pass. Performance unchanged at 10k rewards/sec. Backward
 666 | compatibility warnings added for deprecated methods.
 667 | 
 668 | Files changed:
 669 | - `areal/api/reward_api.py:12`: Consolidate compute/compute_batch
 670 | - `areal/reward/gsm8k.py`: Update to new API
 671 | - `areal/reward/code_reward.py`: Update to new API
 672 | - `areal/reward/geometry3k.py`: Update to new API
 673 | - `docs/customization/reward.md`: Update documentation
 674 | - `docs/migration/reward_api.md`: Migration guide
 675 | - `examples/custom_reward.py`: Update example
 676 | ```
 677 | 
 678 | ## Error Handling
 679 | 
 680 | ### Rebase Conflicts
 681 | 
 682 | If rebase fails:
 683 | 
 684 | 1. Show conflict files
 685 | 1. Provide resolution instructions
 686 | 1. Wait for user to resolve
 687 | 1. After resolution, continue with squashing step
 688 | 1. Offer to abort rebase if needed: `git rebase --abort`
 689 | 
 690 | ### Squash Failures
 691 | 
 692 | If squash/commit fails:
 693 | 
 694 | 1. Check if there are changes to commit: `git status`
 695 | 1. Verify no conflicts remain: `git diff --cached`
 696 | 1. If needed, abort and return to pre-rebase state
 697 | 
 698 | ### Push Failures
 699 | 
 700 | If force push fails:
 701 | 
 702 | 1. Verify remote branch exists
 703 | 1. Check GitHub authentication: `gh auth status`
 704 | 1. Confirm branch protection rules allow force push
 705 | 1. **For fork workflow**: Verify the fork remote URL is correct and you have push access
 706 | 1. Provide manual push instructions if needed:
 707 |    ```bash
 708 |    # Fork workflow
 709 |    git push -f -u <fork-remote> <branch>
 710 |    # Maintainer workflow
 711 |    git push -f -u origin <branch>
 712 |    ```
 713 | 
 714 | ### PR Creation/Update Failures
 715 | 
 716 | If `gh pr create` or `gh pr edit` fails:
 717 | 
 718 | 1. Check if PR already exists: `gh pr view`
 719 | 1. Verify GitHub authentication: `gh auth status`
 720 | 1. Check for branch protection rules
 721 | 1. Provide manual PR creation/update link
 722 | 
 723 | ## Safety Checks
 724 | 
 725 | **Before Starting:**
 726 | 
 727 | - Confirm no uncommitted changes
 728 | - Confirm not on main/master branch
 729 | - Check for existing PR and get user permission to overwrite if exists
 730 | - Backup branch: `git branch backup/$(git branch --show-current)-$(date +%s)`
 731 | 
 732 | **Before Rebase:**
 733 | 
 734 | - Fetch latest from origin
 735 | - Show divergence summary
 736 | 
 737 | **Before Squash:**
 738 | 
 739 | - Show commits that will be squashed
 740 | - Confirm user wants to proceed
 741 | 
 742 | **Before Force Push:**
 743 | 
 744 | - **CRITICAL**: Warn user that force push will rewrite history
 745 | - Show current commit that will replace remote history
 746 | - Confirm branch name
 747 | - If PR exists, emphasize that PR history will be rewritten
 748 | 
 749 | **Before PR Creation/Update:**
 750 | 
 751 | - Show full preview of title/description
 752 | - Confirm target branch
 753 | - If updating existing PR, show what will change
 754 | 
 755 | ______________________________________________________________________
 756 | 
 757 | <!--
 758 | ================================================================================
 759 |                             MAINTAINER GUIDE
 760 | ================================================================================
 761 | 
 762 | Location: .claude/commands/create-pr.md
 763 | Invocation: /create-pr
 764 | 
 765 | ## Design Philosophy
 766 | 
 767 | - Automates full PR creation workflow: detect remote, fetch, rebase, **squash to single commit**, push, create/update PR
 768 | - **Supports both maintainer and fork workflows**:
 769 |   - Maintainer: push to `origin`, create PR within same repo
 770 |   - Fork: push to fork remote, create cross-repo PR to upstream
 771 | - **Always squashes all commits** since `origin/main` into a single commit with message generated via the `commit-conventions` skill
 772 | - **Handles existing PRs** by detecting them and force-updating after user permission
 773 | - Follows repository's Conventional Commits format
 774 | - Requires user confirmation at critical steps (existing PR detection, rebase, squash, force-push, PR creation/update)
 775 | - Generates intelligent commit messages, PR titles, and descriptions based on change analysis
 776 | - Uses force push (`-f`) by design, as squashing requires rewriting history
 777 | 
 778 | ## How to Update
 779 | 
 780 | ### Adding New Scopes
 781 | Update "Determine Scope" section with new file path mappings.
 782 | 
 783 | ### Changing PR Template
 784 | Update "PR Description Format" section with new template structure.
 785 | 
 786 | ### Modifying Workflow Steps
 787 | Update relevant "Step N" sections with new git commands or logic.
 788 | 
 789 | ================================================================================
 790 | -->
```


---
## .claude/commands/gen-commit-msg.md

```
   1 | ---
   2 | name: gen-commit-msg
   3 | description: Generate intelligent commit messages based on staged changes. Invoke with /gen-commit-msg.
   4 | ---
   5 | 
   6 | # Generate Commit Message
   7 | 
   8 | Generate a well-formatted commit message based on staged changes.
   9 | 
  10 | ## Usage
  11 | 
  12 | ```
  13 | /gen-commit-msg [--amend] [--scope <scope>]
  14 | ```
  15 | 
  16 | **Arguments:**
  17 | 
  18 | - `--amend`: Amend the previous commit instead of creating new
  19 | - `--scope <scope>`: Force a specific scope (e.g., `workflow`, `engine`)
  20 | 
  21 | ## Workflow
  22 | 
  23 | ### Step 1: Analyze Changes
  24 | 
  25 | ```bash
  26 | # Check staged files
  27 | git diff --cached --name-only
  28 | 
  29 | # Check staged content
  30 | git diff --cached
  31 | 
  32 | # Check recent commit style
  33 | git log --oneline -5
  34 | ```
  35 | 
  36 | ### Step 2: Categorize Changes
  37 | 
  38 | | Type       | When to Use                     |
  39 | | ---------- | ------------------------------- |
  40 | | `feat`     | New feature or capability       |
  41 | | `fix`      | Bug fix                         |
  42 | | `docs`     | Documentation only              |
  43 | | `refactor` | Code change without feature/fix |
  44 | | `test`     | Adding or fixing tests          |
  45 | | `chore`    | Build, deps, config changes     |
  46 | | `perf`     | Performance improvement         |
  47 | 
  48 | ### Step 3: Determine Scope
  49 | 
  50 | Infer scope from changed files:
  51 | 
  52 | - `areal/workflow/` → `workflow`
  53 | - `areal/engine/` → `engine`
  54 | - `areal/reward/` → `reward`
  55 | - `areal/dataset/` → `dataset`
  56 | - `areal/api/` → `api`
  57 | - `docs/` → `docs`
  58 | - Multiple areas → omit scope or use broader term
  59 | 
  60 | ### Step 4: Generate Message
  61 | 
  62 | **Format:**
  63 | 
  64 | ```
  65 | <type>(<scope>): <subject>
  66 | 
  67 | <body>
  68 | 
  69 | [Optional sections:]
  70 | Key changes:
  71 | - change 1
  72 | - change 2
  73 | 
  74 | Refs: #123, #456
  75 | ```
  76 | 
  77 | **Rules:**
  78 | 
  79 | - Subject: imperative mood, ~50-72 chars, no period
  80 | - Body: explain "why" not "what", wrap at 72 chars
  81 | - Key changes: bullet list of main modifications (for complex commits)
  82 | - Refs: reference issues/PRs if applicable
  83 | 
  84 | ### Step 5: Confirm and Commit
  85 | 
  86 | Show preview:
  87 | 
  88 | ```
  89 | ─────────────────────────────────────
  90 | feat(workflow): add vision support to RLVR
  91 | 
  92 | Add VisionRLVRWorkflow for vision-language RL training.
  93 | Supports image inputs alongside text prompts.
  94 | ─────────────────────────────────────
  95 | ```
  96 | 
  97 | Ask user to confirm, then execute:
  98 | 
  99 | ```bash
 100 | git commit -m "$(cat <<'EOF'
 101 | <message>
 102 | EOF
 103 | )"
 104 | ```
 105 | 
 106 | ## Examples
 107 | 
 108 | **Single file fix:**
 109 | 
 110 | ```
 111 | fix(reward): handle empty completion in gsm8k
 112 | 
 113 | Return 0 reward instead of raising exception when
 114 | completion string is empty after extraction.
 115 | ```
 116 | 
 117 | **Multi-file feature:**
 118 | 
 119 | ```
 120 | feat(engine): add CPU offload support to ArchonEngine
 121 | 
 122 | Enable torch_memory_saver for model offloading during
 123 | rollout phase to reduce GPU memory pressure.
 124 | 
 125 | Key changes:
 126 | - Add offload/onload methods to ArchonEngine
 127 | - Integrate with weight update flow
 128 | - Handle ROCm compatibility
 129 | ```
 130 | 
 131 | **Docs only:**
 132 | 
 133 | ```
 134 | docs: update algorithm comparison table
 135 | 
 136 | Add SAPO and GSPO to the algorithm family documentation
 137 | with configuration examples.
 138 | ```
 139 | 
 140 | ______________________________________________________________________
 141 | 
 142 | <!--
 143 | ================================================================================
 144 |                             MAINTAINER GUIDE
 145 | ================================================================================
 146 | 
 147 | Location: .claude/commands/gen-commit-msg.md
 148 | Invocation: /gen-commit-msg
 149 | 
 150 | ## Design Philosophy
 151 | 
 152 | - Automates commit message generation following Conventional Commits format
 153 | - Matches repository's existing style
 154 | - Requires user confirmation before commit
 155 | 
 156 | ## How to Update
 157 | 
 158 | ### Adding New Scopes
 159 | Update "Determine Scope" section with new file path mappings.
 160 | 
 161 | ### Changing Format
 162 | Update "Generate Message" format template and rules.
 163 | 
 164 | ================================================================================
 165 | -->
```


---
## .claude/commands/review-pr.md

```
   1 | ---
   2 | name: review-pr
   3 | description: Intelligent PR code review with dynamic agent allocation based on change types
   4 | allowed-tools: Read, Grep, Glob, Bash, Task
   5 | ---
   6 | 
   7 | <!-- Reference data (auto-loaded via @import) -->
   8 | 
   9 | @.claude/data/review-pr-change-types.md @.claude/data/review-pr-templates.md
  10 | 
  11 | # PR Code Review (Dynamic Agent Allocation)
  12 | 
  13 | Intelligent code review for the current branch's Pull Request. Dynamically generates
  14 | targeted review tasks based on PR changes.
  15 | 
  16 | ## Arguments
  17 | 
  18 | `$ARGUMENTS`
  19 | 
  20 | - No arguments: Review PR for current branch
  21 | - PR number: Review specific PR (e.g., `/review-pr 123`)
  22 | - `--quick`: Quick mode, only run Phase 1 analysis
  23 | 
  24 | ## Quick Start
  25 | 
  26 | 1. Get current branch PR: `gh pr view --json number,title,state,isDraft`
  27 | 1. If PR doesn't exist or is closed, stop and explain
  28 | 1. Execute Phases 1-4 in order
  29 | 
  30 | ## Workflow Overview
  31 | 
  32 | ```
  33 | Phase 1: Deep PR Analysis [Haiku + Sonnet]
  34 |     |- 1.0 PR Status Check [Haiku]
  35 |     |- 1.1 Get PR Summary [Haiku]
  36 |     +- 1.2-1.4 Change Type Detection [Sonnet]
  37 |     |
  38 | Phase 2: Dynamic Agent Planning [Sonnet]
  39 |     |
  40 | Phase 3: Execute Review Tasks [Parallel, Dynamic Model Selection]
  41 |     |
  42 | Phase 4: Confidence Scoring & Summary [Haiku]
  43 | ```
  44 | 
  45 | ## Model Configuration
  46 | 
  47 | | Mode                      | CRITICAL/HIGH | MEDIUM | LOW    |
  48 | | ------------------------- | ------------- | ------ | ------ |
  49 | | **Default**               | Opus          | Sonnet | Haiku  |
  50 | | **Quick** (`--quick`)     | Sonnet        | Sonnet | Sonnet |
  51 | | **Economy** (`--economy`) | Sonnet        | Haiku  | Haiku  |
  52 | 
  53 | ______________________________________________________________________
  54 | 
  55 | ## Phase 1: Deep PR Analysis
  56 | 
  57 | ### 1.0 PR Status Check \[Haiku\]
  58 | 
  59 | Check if PR should be reviewed:
  60 | 
  61 | - Is it closed? -> Stop
  62 | - Is it a draft? -> Note but continue
  63 | - Is it bot-generated? -> Skip
  64 | 
  65 | ### 1.1 Get PR Summary \[Haiku\]
  66 | 
  67 | Get basic PR info: title, description, modified files, change summary.
  68 | 
  69 | ### 1.2 Change Type Detection \[Sonnet\]
  70 | 
  71 | Analyze each file change, detecting change types by risk level.
  72 | 
  73 | **Reference**: See `review-pr-change-types.md` for complete detection tables:
  74 | 
  75 | - CRITICAL level types (Archon, FSDP, Megatron, DCP)
  76 | - HIGH level types (distributed comm, DTensor, MoE, TP/EP/CP)
  77 | - MEDIUM level types (tensor ops, workflow, API, compile)
  78 | - LOW level types (tests, docs, config)
  79 | 
  80 | ### 1.3 Framework-Specific Risk Identification
  81 | 
  82 | Based on detected types, identify corresponding risks.
  83 | 
  84 | **Reference**: See `review-pr-change-types.md` for risk lists per framework.
  85 | 
  86 | ### 1.4 Output Change Analysis Report
  87 | 
  88 | ```
  89 | CHANGE_ANALYSIS_REPORT:
  90 | - detected_types: [ARCHON_PARALLEL, EP_ETP, FSDP_CORE, ...]
  91 | - risk_level: CRITICAL | HIGH | MEDIUM | LOW
  92 | - affected_files: [file1.py, file2.py, ...]
  93 | - identified_risks: [risk1, risk2, ...]
  94 | - related_frameworks: [archon, fsdp, megatron, ...]
  95 | ```
  96 | 
  97 | ______________________________________________________________________
  98 | 
  99 | ## Phase 2: Dynamic Agent Planning \[Sonnet\]
 100 | 
 101 | ### 2.1 Planning Principles
 102 | 
 103 | 1. **Generate tasks by risk area**: Each high-risk area gets a dedicated task
 104 | 1. **Merge related changes**: Interdependent changes can be merged
 105 | 1. **Model selection**: CRITICAL/HIGH -> Opus, MEDIUM -> Sonnet, LOW -> Haiku
 106 | 1. **Minimum coverage**: Even simple changes get at least 1 basic review task
 107 | 
 108 | ### 2.2 Task Template Selection
 109 | 
 110 | Based on detected change types, select appropriate review task templates.
 111 | 
 112 | **Reference**: See `review-pr-templates.md` for complete task templates:
 113 | 
 114 | - Framework-specific tasks (Archon, FSDP, Megatron, DCP, Trainer)
 115 | - General tasks (Logic, Concurrency, Tensor, Numerical, TP, etc.)
 116 | 
 117 | ### 2.3 Output Review Task List
 118 | 
 119 | ```
 120 | GENERATED_REVIEW_TASKS:
 121 | 1. [Opus] Task Name
 122 |    - Reason: XXX change type detected
 123 |    - Checklist: [...]
 124 |    - Focus files: [...]
 125 | 
 126 | 2. [Sonnet] Task Name
 127 |    - Reason: ...
 128 |    ...
 129 | ```
 130 | 
 131 | ______________________________________________________________________
 132 | 
 133 | ## Phase 3: Execute Review Tasks \[Parallel\]
 134 | 
 135 | ### 3.1 Execution Rules
 136 | 
 137 | - Use Phase 2 specified model for each task
 138 | - Execute all agents **in parallel**
 139 | - Each agent reviews independently
 140 | 
 141 | ### 3.2 Agent Output Format
 142 | 
 143 | ```
 144 | REVIEW_RESULT:
 145 | task_name: "Task Name"
 146 | model: Opus | Sonnet | Haiku
 147 | findings:
 148 |   - issue: "Issue description"
 149 |     severity: CRITICAL | HIGH | MEDIUM | LOW
 150 |     file: "path/to/file.py"
 151 |     line: 123
 152 |     code_snippet: |
 153 |       Relevant code snippet
 154 |     reason: "Why this is an issue"
 155 |     suggestion: "Fix suggestion"
 156 | ```
 157 | 
 158 | ### 3.3 Review Depth by Model
 159 | 
 160 | | Model      | Requirements                                                               |
 161 | | ---------- | -------------------------------------------------------------------------- |
 162 | | **Opus**   | Complete context, cross-file traces, verify parallel strategy interactions |
 163 | | **Sonnet** | Changed code + direct callers/callees, type signature consistency          |
 164 | | **Haiku**  | Format and basic correctness only                                          |
 165 | 
 166 | ______________________________________________________________________
 167 | 
 168 | ## Phase 4: Confidence Scoring & Summary \[Haiku\]
 169 | 
 170 | ### 4.1 Confidence Scoring (0-100)
 171 | 
 172 | | Score   | Meaning                               |
 173 | | ------- | ------------------------------------- |
 174 | | **0**   | False positive or pre-existing issue  |
 175 | | **25**  | May be real, cannot verify            |
 176 | | **50**  | Real but minor or rare                |
 177 | | **75**  | Very likely real, important           |
 178 | | **100** | Confirmed real, will frequently occur |
 179 | 
 180 | ### 4.2 Summary Report Format
 181 | 
 182 | ```markdown
 183 | # PR Review Summary
 184 | 
 185 | ## PR Overview
 186 | - **Title**: PR title
 187 | - **Detected Change Types**: [...]
 188 | - **Risk Level**: CRITICAL | HIGH | MEDIUM | LOW
 189 | - **Generated Review Tasks**: N
 190 | 
 191 | ## Executed Review Tasks
 192 | | # | Model | Task Name | Reason |
 193 | |---|-------|-----------|--------|
 194 | 
 195 | ## Findings
 196 | 
 197 | ### CRITICAL Severity (Confidence >= 75)
 198 | #### Issue 1: [Title]
 199 | - **File**: `path/to/file.py:123`
 200 | - **Confidence**: 85
 201 | - **Description**: ...
 202 | - **Fix Suggestion**: ...
 203 | 
 204 | ### HIGH Severity (Confidence >= 50)
 205 | ...
 206 | 
 207 | ## Review Statistics
 208 | - Total issues: X (CRITICAL: X, HIGH: X, MEDIUM: X, LOW: X)
 209 | - Filtered false positives: X
 210 | ```
 211 | 
 212 | ### 4.3 Output Integrity (CRITICAL)
 213 | 
 214 | The Phase 4 summary report is the **FINAL DELIVERABLE** of this command.
 215 | 
 216 | - Output the COMPLETE report exactly as specified in Section 4.2 -- every section, every
 217 |   finding, every field.
 218 | - Do NOT abbreviate, summarize, or compress any part of the report.
 219 | - Do NOT omit findings, code snippets, fix suggestions, or statistics.
 220 | - If the report is long, that is expected and correct -- **completeness > brevity**.
 221 | - The orchestrating agent receiving this output MUST present it **VERBATIM** to the
 222 |   user. No re-summarization, no condensing, no "brief version".
 223 | 
 224 | ______________________________________________________________________
 225 | 
 226 | ## Dynamic Generation Examples
 227 | 
 228 | | PR Type        | Detected Types                        | Generated Tasks |
 229 | | -------------- | ------------------------------------- | --------------- |
 230 | | Docs only      | \[DOCS\]                              | 1 Haiku         |
 231 | | Config only    | \[CONFIG_ONLY\]                       | 1-2 Haiku       |
 232 | | Single bug fix | \[TENSOR_OPS\]                        | 2-4 Sonnet      |
 233 | | Archon core    | \[ARCHON\_\*, EP_ETP, DTENSOR\]       | 4-8 Opus        |
 234 | | Cross-domain   | \[WORKFLOW_ENGINE, FSDP_CORE, TESTS\] | 5-10 mixed      |
 235 | 
 236 | ______________________________________________________________________
 237 | 
 238 | ## False Positive Guide (Rate Confidence 0)
 239 | 
 240 | - Pre-existing issues (not introduced by this PR)
 241 | - Intentionally designed code that looks like a bug
 242 | - Issues linter/compiler would catch
 243 | - Issues on lines user didn't modify
 244 | - Explicitly disabled issues (lint ignore comments)
 245 | 
 246 | ______________________________________________________________________
 247 | 
 248 | ## Important Notes
 249 | 
 250 | - **Do NOT** check build signals or try to build/type-check
 251 | - Use `gh` to interact with GitHub, not web fetch
 252 | - **Do NOT** automatically post comments to PR
 253 | - Must provide file path and line number when referencing issues
 254 | 
 255 | ______________________________________________________________________
 256 | 
 257 | <!--
 258 | ================================================================================
 259 |                             MAINTAINER GUIDE
 260 | ================================================================================
 261 | 
 262 | Location: .claude/commands/review-pr.md
 263 | Invocation: /review-pr
 264 | Related files:
 265 |   - .claude/data/review-pr-change-types.md: Change type detection tables
 266 |   - .claude/data/review-pr-templates.md: Review task templates
 267 | 
 268 | ## Structure
 269 | 
 270 | - Main file (this): workflow and phases, @imports data files
 271 | - data/review-pr-change-types.md: detection tables
 272 | - data/review-pr-templates.md: task templates
 273 | 
 274 | ## How to Update
 275 | 
 276 | ### Adding New Change Types
 277 | Edit .claude/data/review-pr-change-types.md:
 278 | 1. Add to appropriate level table (CRITICAL/HIGH/MEDIUM/LOW)
 279 | 2. Add framework risks if applicable
 280 | 
 281 | ### Adding New Task Templates
 282 | Edit .claude/data/review-pr-templates.md:
 283 | 1. Add to framework-specific or general section
 284 | 2. Include checklist
 285 | 
 286 | ### Adjusting Model Selection
 287 | Modify "Model Configuration" table in this file.
 288 | 
 289 | ================================================================================
 290 | -->
```


---
## .claude/commands/translate-doc-zh.md

```
   1 | ---
   2 | name: translate-doc-zh
   3 | description: 'Translate English documentation to Chinese. Usage: /translate-doc-zh docs/en/path/to/file.md'
   4 | argument-hint: <path-to-en-doc>
   5 | ---
   6 | 
   7 | # Document Translation (EN → ZH)
   8 | 
   9 | Translate English documentation to Chinese for the AReaL project.
  10 | 
  11 | ## Usage
  12 | 
  13 | ```
  14 | /translate-doc-zh $ARGUMENTS
  15 | ```
  16 | 
  17 | **Arguments (`$ARGUMENTS`):**
  18 | 
  19 | - Path to English document (e.g., `docs/en/tutorial/quickstart.md`)
  20 | 
  21 | ## Document to Translate
  22 | 
  23 | !`if [ -f "$ARGUMENTS" ]; then echo "File: $ARGUMENTS"; echo ""; head -50 "$ARGUMENTS"; else echo "ERROR: File not found: $ARGUMENTS"; echo "Please provide a valid path to an English document in docs/en/"; fi`
  24 | 
  25 | ## Workflow
  26 | 
  27 | ### Step 1: Validate the Path
  28 | 
  29 | 1. Check if `$ARGUMENTS` exists
  30 | 1. Verify it is inside `docs/en/` directory and ends with `.md`
  31 | 1. If invalid, inform user and stop
  32 | 
  33 | ### Step 2: Determine Output Path
  34 | 
  35 | - Input: `$ARGUMENTS` (e.g., `docs/en/tutorial/quickstart.md`)
  36 | - Output: Replace `docs/en/` with `docs/zh/` (e.g., `docs/zh/tutorial/quickstart.md`)
  37 | 
  38 | ### Step 3: Check if Chinese Document Exists
  39 | 
  40 | - If `docs/zh/<path>` exists → **Modification Scenario**
  41 | - If `docs/zh/<path>` does NOT exist → **Full Translation Scenario**
  42 | 
  43 | ______________________________________________________________________
  44 | 
  45 | ## Scenario 1: Modification (Chinese Document Exists)
  46 | 
  47 | Use when Chinese document already exists.
  48 | 
  49 | ### Workflow
  50 | 
  51 | 1. Read both English and Chinese documents
  52 | 1. Compare differences to identify:
  53 |    - New sections in English
  54 |    - Modified sections in English
  55 |    - Deleted sections
  56 | 1. Translate only changed parts
  57 | 1. Preserve all other Chinese content unchanged
  58 | 
  59 | **Translation Rules:**
  60 | 
  61 | - Preserve English technical terms: FSDP, FSDP2, GRPO, PPO, DAPO, MoE, LLM, RL, RLVR,
  62 |   Claude Code, OpenCode, Megatron, Archon, SGLang, vLLM, PyTorch, HuggingFace,
  63 |   Transformers, etc.
  64 | - File paths and code examples remain unchanged
  65 | - Professional and rigorous terminology
  66 | - Preserve Markdown format, code blocks, tables
  67 | 
  68 | ______________________________________________________________________
  69 | 
  70 | ## Scenario 2: Full Translation (Chinese Document Does NOT Exist)
  71 | 
  72 | Use when Chinese document does not exist.
  73 | 
  74 | ### Workflow
  75 | 
  76 | 1. Read the English source document
  77 | 1. Translate entire document to Chinese
  78 | 
  79 | **Translation Rules:**
  80 | 
  81 | - Preserve English technical terms: FSDP, FSDP2, GRPO, PPO, DAPO, MoE, LLM, RL, RLVR,
  82 |   Claude Code, OpenCode, Megatron, Archon, SGLang, vLLM, PyTorch, HuggingFace,
  83 |   Transformers, etc.
  84 | - File paths and code examples remain unchanged
  85 | - Professional and rigorous terminology
  86 | - Preserve Markdown format, code blocks, tables
  87 | 
  88 | 3. Create new Chinese document at `docs/zh/<path>`
  89 | 
  90 | ______________________________________________________________________
  91 | 
  92 | ## Error Handling
  93 | 
  94 | ### Invalid Path
  95 | 
  96 | If user provides an invalid path:
  97 | 
  98 | 1. Tell user the file does not exist
  99 | 1. Ask user to provide a valid path starting with `docs/en/` and ending with `.md`
 100 | 
 101 | ### Write Failure
 102 | 
 103 | If target directory does not exist:
 104 | 
 105 | 1. Create the directory first using Bash mkdir -p
 106 | 1. Then write the file
```


---
## .claude/commands/update-docker-image.md

```
   1 | ---
   2 | name: update-docker-image
   3 | description: Update the Dockerfile given package versions, and use GitHub CI to build and test the new image.
   4 | argument-hint: <package-versions>
   5 | ---
   6 | 
   7 | ## Usage
   8 | 
   9 | ```
  10 | /update-docker-image $ARGUMENTS
  11 | ```
  12 | 
  13 | **Arguments (`$VERSION`):** a list of pinned package versions, such as "sglang==0.5.9
  14 | vllm==0.10.1 torch==2.10.1"
  15 | 
  16 | ## Architecture
  17 | 
  18 | The Dockerfile produces two image variants from a single file:
  19 | 
  20 | - `ghcr.io/inclusionai/areal-runtime:{tag}-sglang` — SGLang inference backend
  21 | - `ghcr.io/inclusionai/areal-runtime:{tag}-vllm` — vLLM inference backend
  22 | 
  23 | Both variants share the same base image (`lmsysorg/sglang:…`) and identical layers up to
  24 | STAGE 3. Only `ARG VARIANT` (declared late for cache efficiency) controls which
  25 | inference backend is installed via `--extra ${VARIANT}`.
  26 | 
  27 | The `latest` tag always points to the sglang variant.
  28 | 
  29 | ## Workflow
  30 | 
  31 | 1. **Validate versions.** Update the version requirements in @pyproject.toml according
  32 |    to the input. Validate that the provided versions exist in the pip registry.
  33 |    Otherwise, exit and raise an error report to the user. Keep other dependency versions
  34 |    unchanged in this step.
  35 | 
  36 | 1. **Check upstream dependency compatibility.** For the following packages, browse the
  37 |    GitHub repo and check for dependency version mismatches with AReaL:
  38 | 
  39 |    - For sglang, check
  40 |      `https://github.com/sgl-project/sglang/blob/v${version}/python/pyproject.toml`
  41 |    - For vllm, check
  42 |      `https://github.com/vllm-project/vllm/blob/v${version}/pyproject.toml`
  43 | 
  44 |    Focus on the verions of following packages in particular:
  45 | 
  46 |    - torch
  47 |    - transformers
  48 | 
  49 | 1. **Resolve dependency conflicts** and report to user.
  50 | 
  51 |    If there's no inconsistency between the above packages, and it only conflicts with
  52 |    AReaL, update AReaL's version.
  53 | 
  54 |    If the above packages have mutual conflict, summarize and report to user, then you
  55 |    MUST ask the user for resolution.
  56 | 
  57 |    Output format:
  58 | 
  59 |    ```
  60 |    Summary
  61 | 
  62 |    ---
  63 |    Updated Packages (no actions required):
  64 |    - ${name}, ${packageA} requires ${packageAVersion}, ${packageB} requires ${packageBVersion}, AReaL specified ${version}, updated to ${version}
  65 |    - ...
  66 | 
  67 |    ---
  68 |    Mismatched Packages (need to resolve):
  69 | 
  70 |    - ${name}, ${packageA} requires ${packageAVersion}, ${packageB} requires ${packageBVersion}
  71 |    - ...
  72 |    ```
  73 | 
  74 | 1. **Update @pyproject.toml** according to the user's conflict resolution. You may use
  75 |    `override-dependencies` in `[tool.uv]` to force-pin versions where needed. Remember
  76 |    that `sglang` and `vllm` are declared as **conflicting extras** — never install both.
  77 | 
  78 | 1. **Validate** that the conflicts in step 3 have been all resolved. If not, return to
  79 |    step 3 and you MUST ask the user again.
  80 | 
  81 | 1. **Lock dependencies.** Run `uv lock` to regenerate `uv.lock`. If errors occur, return
  82 |    to step 3 — you must ask the user for resolution before modifying and trying again.
  83 | 
  84 | 1. **Update the Dockerfile** if needed. The Dockerfile uses only `ARG VARIANT` (no
  85 |    `ARG BASE_IMAGE`) to select between sglang and vllm. All layers before the VARIANT
  86 |    declaration are shared between both variants for Docker cache efficiency.
  87 | 
  88 |    Only modify the Dockerfile if the base image, system packages, or build steps need to
  89 |    change (e.g., new base image URL, new CUDA version). Do NOT modify it just for
  90 |    pyproject.toml version bumps — `uv pip install -r pyproject.toml` handles that
  91 |    automatically.
  92 | 
  93 | 1. **Create a PR and trigger CI.** Use the `/create-pr` command to create a PR, then
  94 |    trigger the CI workflow manually via `.github/workflows/build-docker-image.yml`.
  95 | 
  96 |    The docker build CI builds both sglang and vllm images, then automatically triggers
  97 |    testing on each. Debug until the overall workflow succeeds.
  98 | 
  99 |    If you encounter issues that cannot be resolved, ask the user for help.
```


---
## .claude/commands/upgrade-megatron-core.md

```
   1 | ---
   2 | name: upgrade-megatron-core
   3 | description: Upgrade Megatron-Core version in AReaL. Audits all megatron.core and mbridge API usage, cross-references upstream source, and updates call sites.
   4 | argument-hint: <version>
   5 | ---
   6 | 
   7 | ## Usage
   8 | 
   9 | ```
  10 | /upgrade-megatron-core $ARGUMENTS
  11 | ```
  12 | 
  13 | **Arguments (`$VERSION`):** Target Megatron-Core version tag or commit hash, e.g.
  14 | `v0.12.0`, `core_r0.12.0`, or a commit SHA. If not given, get the required version from
  15 | AReaL's "pyproject.toml" and check whether the current code is fully compatible with the
  16 | specified version.
  17 | 
  18 | ## Prerequisites — Source Code for Cross-Referencing
  19 | 
  20 | This command requires upstream source repos to cross-reference API signatures.
  21 | 
  22 | ### Megatron-LM
  23 | 
  24 | ```bash
  25 | MCORE_DIR="${REPO_ROOT}/Megatron-LM"
  26 | # Validate VERSION to prevent command injection
  27 | if [[ ! "$VERSION" =~ ^[a-zA-Z0-9._/-]+$ ]]; then
  28 |   echo "Error: Invalid version format: $VERSION"
  29 |   exit 1
  30 | fi
  31 | if [ ! -d "$MCORE_DIR" ]; then
  32 |   git clone --depth 1 --branch "${VERSION}" https://github.com/NVIDIA/Megatron-LM.git "$MCORE_DIR"
  33 | else
  34 |   cd "$MCORE_DIR" && git fetch origin && git checkout "${VERSION}" && cd -
  35 | fi
  36 | ```
  37 | 
  38 | If cloning or checkout fails, report to the user immediately.
  39 | 
  40 | The relevant upstream source paths are:
  41 | 
  42 | - `Megatron-LM/megatron/core/parallel_state.py`
  43 | - `Megatron-LM/megatron/core/distributed/`
  44 | - `Megatron-LM/megatron/core/optimizer/`
  45 | - `Megatron-LM/megatron/core/optimizer_param_scheduler.py`
  46 | - `Megatron-LM/megatron/core/pipeline_parallel/`
  47 | - `Megatron-LM/megatron/core/transformer/`
  48 | - `Megatron-LM/megatron/core/models/gpt/`
  49 | - `Megatron-LM/megatron/core/fp8_utils.py`
  50 | - `Megatron-LM/megatron/core/dist_checkpointing/`
  51 | - `Megatron-LM/megatron/core/packed_seq_params.py`
  52 | - `Megatron-LM/megatron/core/utils.py`
  53 | 
  54 | ### mbridge
  55 | 
  56 | mbridge wraps megatron.core for HF↔MCore weight conversion. AReaL depends on its
  57 | internal APIs for weight loading/saving, so mbridge must also be audited when upgrading
  58 | megatron-core.
  59 | 
  60 | ```bash
  61 | MBRIDGE_DIR="${REPO_ROOT}/mbridge-src"
  62 | # Determine the compatible mbridge version from pyproject.toml
  63 | MBRIDGE_VER=$(grep 'mbridge' "${REPO_ROOT}/pyproject.toml" | grep -oP '\d+\.\d+\.\d+')
  64 | if [ ! -d "$MBRIDGE_DIR" ]; then
  65 |   git clone --branch "v${MBRIDGE_VER}" https://github.com/ISEEKYAN/mbridge.git "$MBRIDGE_DIR"
  66 | else
  67 |   cd "$MBRIDGE_DIR" && git fetch origin && git checkout "v${MBRIDGE_VER}" && cd -
  68 | fi
  69 | ```
  70 | 
  71 | The relevant mbridge source paths are:
  72 | 
  73 | - `mbridge-src/mbridge/__init__.py` — top-level exports (`AutoBridge`)
  74 | - `mbridge-src/mbridge/core/bridge.py` — `Bridge` base class: `get_model()`,
  75 |   `load_weights()`, `save_weights()`, `export_weights()`, `set_extra_args()`, all
  76 |   `_weight_*` private methods
  77 | - `mbridge-src/mbridge/core/auto_bridge.py` — `AutoBridge.from_pretrained()`,
  78 |   `from_config()`
  79 | - `mbridge-src/mbridge/core/llm_bridge.py` — `LLMBridge`: `_build_base_config()`,
  80 |   `_get_gptmodel_args()`, `_get_transformer_layer_spec()`, `_model_provider()`
  81 | - `mbridge-src/mbridge/core/vlm_bridge.py` — `VLMBridge` (not directly used but may
  82 |   affect inheritance)
  83 | - `mbridge-src/mbridge/core/util.py` — `get_model()`, `unwrap_model()`,
  84 |   `broadcast_from_megatron_pp()`, `preprocess_packed_seqs()`,
  85 |   `postprocess_packed_seqs()`
  86 | - `mbridge-src/mbridge/core/parallel_states.py` — `ParallelStates` dataclass (wraps
  87 |   `mpu.*` getters)
  88 | - `mbridge-src/mbridge/utils/post_creation_callbacks.py` — `make_value_model()`,
  89 |   `freeze_moe_router()`
  90 | 
  91 | ______________________________________________________________________
  92 | 
  93 | ## Affected Files
  94 | 
  95 | ### Primary (engine layer — most likely to break)
  96 | 
  97 | | File                                                     | Imports                                                                                                                                                                                                           |
  98 | | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  99 | | `areal/engine/megatron_engine.py`                        | `parallel_state`, `tensor_parallel`, `DDP`, `finalize_model_grads`, `OptimizerConfig`, `get_megatron_optimizer`, `OptimizerParamScheduler`, `get_forward_backward_func`, `TransformerConfig`, `get_model_config`  |
 100 | | `areal/engine/megatron_utils/megatron.py`                | `parallel_state`, `is_float8tensor`, `TransformerConfig`, `get_transformer_layer_offset`                                                                                                                          |
 101 | | `areal/engine/megatron_utils/checkpointer.py`            | `dist_checkpointing`, `mpu`, `tensor_parallel`, `ShardedObject`, `get_default_load_sharded_strategy`, `get_default_save_sharded_strategy`, `FullyParallelLoadStrategyWrapper`, `FullyParallelSaveStrategyWrapper` |
 102 | | `areal/engine/megatron_utils/packed_context_parallel.py` | `parallel_state`, `PackedSeqParams`                                                                                                                                                                               |
 103 | | `areal/engine/megatron_utils/pipeline_parallel.py`       | `TransformerConfig`, `PipelineParallelLayerLayout`                                                                                                                                                                |
 104 | | `areal/engine/megatron_utils/fp8/tensor_helper.py`       | `is_float8tensor`                                                                                                                                                                                                 |
 105 | 
 106 | ### Secondary (model layer)
 107 | 
 108 | | File                                        | Imports                                                                                                                                                 |
 109 | | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
 110 | | `areal/models/mcore/registry.py`            | `tensor_parallel`, `DDP`, `MCoreDDPConfig`, `GPTModel`, `TransformerConfig`                                                                             |
 111 | | `areal/models/mcore/hf_load.py`             | `parallel_state`, `is_float8tensor`                                                                                                                     |
 112 | | `areal/models/mcore/hf_save.py`             | `parallel_state`, `is_float8tensor`                                                                                                                     |
 113 | | `areal/models/mcore/common.py`              | `TransformerConfig`                                                                                                                                     |
 114 | | `areal/models/mcore/qwen3.py`               | `get_gpt_decoder_block_spec`, `TransformerConfig`                                                                                                       |
 115 | | `areal/models/tree_attn/module_megatron.py` | `PackedSeqParams`, `TransformerConfig`, `SelfAttention`, `AttnMaskType`, `TransformerBlockSubmodules`, `TransformerLayer`, `TransformerLayerSubmodules` |
 116 | 
 117 | ### Tertiary (infra + tests — lower risk)
 118 | 
 119 | | File                                                | Imports                                                  |
 120 | | --------------------------------------------------- | -------------------------------------------------------- |
 121 | | `areal/infra/workflow_executor.py`                  | `parallel_state` (conditional import inside method)      |
 122 | | `tests/test_estimate_num_params.py`                 | `parallel_state`, `tensor_parallel`                      |
 123 | | `tests/fp8/engine_utils.py`                         | `parallel_state`                                         |
 124 | | `tests/fp8/model_hooks.py`                          | `parallel_state`                                         |
 125 | | `tests/fp8/test_fp8_rmsnorm.py`                     | `get_fp8_context`, `is_float8tensor`, `get_model_config` |
 126 | | `tests/torchrun/run_megatron_engine_distributed.py` | `parallel_state`                                         |
 127 | 
 128 | ### mbridge files (coupled with megatron.core)
 129 | 
 130 | | File                                        | mbridge Imports                                         |
 131 | | ------------------------------------------- | ------------------------------------------------------- |
 132 | | `areal/engine/megatron_engine.py`           | `mbridge.AutoBridge`                                    |
 133 | | `areal/models/mcore/registry.py`            | `mbridge.core.bridge.Bridge`                            |
 134 | | `areal/models/mcore/hf_load.py`             | `mbridge.core.bridge.Bridge`                            |
 135 | | `areal/models/mcore/hf_save.py`             | `mbridge.core.Bridge`, `mbridge.core.util.unwrap_model` |
 136 | | `areal/models/tree_attn/module_megatron.py` | `mbridge.core.LLMBridge`                                |
 137 | | `tests/test_estimate_num_params.py`         | `mbridge.AutoBridge`                                    |
 138 | 
 139 | ______________________________________________________________________
 140 | 
 141 | ## API Usage Catalog
 142 | 
 143 | For each function/class below, verify the call signature against the upstream source at
 144 | the target version. Focus on: **missing new required parameters**, **removed old
 145 | parameters**, **renamed parameters**, **changed return types**, and **changed method
 146 | signatures on returned objects**.
 147 | 
 148 | ### 1. `megatron.core.parallel_state` (aliased as `mpu`)
 149 | 
 150 | **Source:** `Megatron-LM/megatron/core/parallel_state.py`
 151 | 
 152 | #### `mpu.initialize_model_parallel(...)`
 153 | 
 154 | Called in `megatron_engine.py:186`:
 155 | 
 156 | ```python
 157 | mpu.initialize_model_parallel(
 158 |     tensor_model_parallel_size=...,
 159 |     pipeline_model_parallel_size=...,
 160 |     virtual_pipeline_model_parallel_size=...,
 161 |     use_sharp=False,
 162 |     order="tp-cp-ep-dp-pp",
 163 |     context_parallel_size=...,
 164 |     expert_model_parallel_size=...,
 165 |     expert_tensor_parallel_size=...,
 166 |     distributed_timeout_minutes=...,
 167 | )
 168 | ```
 169 | 
 170 | **Check:** New required params? Renamed params? New parallelism dimensions? Removed
 171 | `use_sharp`? Changed `order` format?
 172 | 
 173 | #### `mpu.destroy_model_parallel()`
 174 | 
 175 | Called in `megatron_engine.py:426` and `tests/test_estimate_num_params.py:60`.
 176 | Straightforward — check for new required params.
 177 | 
 178 | #### Rank/world-size getters
 179 | 
 180 | All of the following are called without arguments unless noted:
 181 | 
 182 | - `mpu.get_data_parallel_rank()` /
 183 |   `mpu.get_data_parallel_rank(with_context_parallel=True)`
 184 | - `mpu.get_data_parallel_world_size()`
 185 | - `mpu.get_data_parallel_group()` /
 186 |   `mpu.get_data_parallel_group(with_context_parallel=True)`
 187 | - `mpu.get_tensor_model_parallel_rank()`
 188 | - `mpu.get_tensor_model_parallel_world_size()`
 189 | - `mpu.get_tensor_model_parallel_group()`
 190 | - `mpu.get_pipeline_model_parallel_rank()`
 191 | - `mpu.get_pipeline_model_parallel_world_size()`
 192 | - `mpu.get_pipeline_model_parallel_group()`
 193 | - `mpu.get_pipeline_model_parallel_last_rank()`
 194 | - `mpu.get_context_parallel_world_size()`
 195 | - `mpu.get_context_parallel_rank()`
 196 | - `mpu.get_context_parallel_group()`
 197 | - `mpu.get_expert_model_parallel_group()`
 198 | - `mpu.get_expert_model_parallel_world_size()`
 199 | - `mpu.get_expert_model_parallel_rank()`
 200 | - `mpu.get_expert_tensor_parallel_world_size()`
 201 | - `mpu.get_expert_tensor_parallel_group()`
 202 | - `mpu.get_expert_tensor_parallel_rank()`
 203 | - `mpu.get_expert_data_parallel_group()`
 204 | - `mpu.get_expert_data_parallel_rank()`
 205 | - `mpu.get_expert_tensor_model_pipeline_parallel_group()`
 206 | - `mpu.get_tensor_and_data_parallel_group(with_context_parallel=True)`
 207 | - `mpu.get_virtual_pipeline_model_parallel_rank()`
 208 | - `mpu.get_virtual_pipeline_model_parallel_world_size()`
 209 | - `mpu.set_virtual_pipeline_model_parallel_rank(vpp_rank)`
 210 | - `mpu.is_initialized()`
 211 | 
 212 | **Check:** Any renamed? Any removed? Any new required keyword-only args? Return type
 213 | changes?
 214 | 
 215 | #### `mpu.is_pipeline_last_stage(...)`
 216 | 
 217 | Called in two forms:
 218 | 
 219 | ```python
 220 | mpu.is_pipeline_last_stage()
 221 | mpu.is_pipeline_last_stage(ignore_virtual=False, vp_stage=model_vp_stage)
 222 | ```
 223 | 
 224 | **Check:** `ignore_virtual` / `vp_stage` params still exist?
 225 | 
 226 | #### `mpu.RankGenerator(...)`
 227 | 
 228 | Called in `megatron_engine.py:912`:
 229 | 
 230 | ```python
 231 | mpu.RankGenerator(tp=..., ep=1, dp=..., pp=..., cp=..., order="tp-cp-ep-dp-pp", rank_offset=0)
 232 | ```
 233 | 
 234 | **Check:** Constructor signature. New params?
 235 | 
 236 | #### `mpu.create_group(ranks, timeout=, pg_options=, group_desc=)`
 237 | 
 238 | Called in `megatron_engine.py:924`.
 239 | 
 240 | **Check:** Signature and kwargs.
 241 | 
 242 | #### `mpu.get_nccl_options(name, nccl_comm_cfgs)`
 243 | 
 244 | Called in `megatron_engine.py:927`:
 245 | 
 246 | ```python
 247 | mpu.get_nccl_options("tp-cp-pp", {})
 248 | ```
 249 | 
 250 | **Check:** Signature change.
 251 | 
 252 | ______________________________________________________________________
 253 | 
 254 | ### 2. `megatron.core.tensor_parallel`
 255 | 
 256 | **Source:** `Megatron-LM/megatron/core/tensor_parallel/`
 257 | 
 258 | #### `tensor_parallel.model_parallel_cuda_manual_seed(seed)`
 259 | 
 260 | Called in `megatron_engine.py:200`, `tests/test_estimate_num_params.py:34`.
 261 | 
 262 | **Check:** Signature.
 263 | 
 264 | #### `tensor_parallel.get_cuda_rng_tracker()`
 265 | 
 266 | Called in `checkpointer.py:172,313`. Returns object with `.get_states()` and
 267 | `.set_states(states)` methods.
 268 | 
 269 | **Check:** Return type still has `get_states()`/`set_states()` methods?
 270 | 
 271 | #### `tensor_parallel.gather_from_sequence_parallel_region(logits, tensor_parallel_output_grad=False)`
 272 | 
 273 | Called in `registry.py:49-51`.
 274 | 
 275 | **Check:** `tensor_parallel_output_grad` kwarg still exists?
 276 | 
 277 | ______________________________________________________________________
 278 | 
 279 | ### 3. `megatron.core.distributed`
 280 | 
 281 | **Source:** `Megatron-LM/megatron/core/distributed/`
 282 | 
 283 | #### `DistributedDataParallel` (DDP)
 284 | 
 285 | Used in `megatron_engine.py` and `registry.py`.
 286 | 
 287 | Constructor called in `registry.py:199`:
 288 | 
 289 | ```python
 290 | DDP(config=tf_config, ddp_config=ddp_config, module=model, disable_bucketing=False)
 291 | ```
 292 | 
 293 | Methods/attributes used:
 294 | 
 295 | - `model_chunk.no_sync` (property/context manager)
 296 | - `model_chunk.start_param_sync` (method)
 297 | - `.zero_grad_buffer()` (called in `megatron_engine.py:543`)
 298 | - `.module` attribute
 299 | - `.vp_stage` attribute (set manually)
 300 | 
 301 | **Check:** Constructor params. `.zero_grad_buffer()` still exists? `no_sync` /
 302 | `start_param_sync` interface?
 303 | 
 304 | #### `DistributedDataParallelConfig` (as `MCoreDDPConfig`)
 305 | 
 306 | Used in `registry.py:198`:
 307 | 
 308 | ```python
 309 | MCoreDDPConfig(**dataclasses.asdict(mcore_config.ddp))
 310 | ```
 311 | 
 312 | **Check:** Dataclass fields. Used fields: `use_distributed_optimizer`,
 313 | `overlap_grad_reduce`, `overlap_param_gather`, `align_param_gather`.
 314 | 
 315 | #### `finalize_model_grads`
 316 | 
 317 | Used in `megatron_engine.py:357`:
 318 | 
 319 | ```python
 320 | model_config.finalize_model_grads_func = finalize_model_grads
 321 | ```
 322 | 
 323 | **Check:** Signature of `finalize_model_grads`. Is it still assigned as a function
 324 | reference to `model_config.finalize_model_grads_func`?
 325 | 
 326 | ______________________________________________________________________
 327 | 
 328 | ### 4. `megatron.core.optimizer`
 329 | 
 330 | **Source:** `Megatron-LM/megatron/core/optimizer/`
 331 | 
 332 | #### `OptimizerConfig` (as `MCoreOptimizerConfig`)
 333 | 
 334 | Constructed in `megatron_engine.py:948`:
 335 | 
 336 | ```python
 337 | MCoreOptimizerConfig(
 338 |     optimizer=..., lr=..., min_lr=..., weight_decay=...,
 339 |     bf16=..., fp16=...,
 340 |     adam_beta1=..., adam_beta2=..., adam_eps=...,
 341 |     use_distributed_optimizer=..., params_dtype=...,
 342 |     clip_grad=..., fp8_recipe=...,
 343 | )
 344 | ```
 345 | 
 346 | Plus post-construction field assignments (lines 963-978):
 347 | 
 348 | - `overlap_param_gather_with_optimizer_step`
 349 | - `use_precision_aware_optimizer`
 350 | - `main_grads_dtype`
 351 | - `main_params_dtype`
 352 | - `exp_avg_dtype`
 353 | - `exp_avg_sq_dtype`
 354 | 
 355 | **Check:** All fields still exist? New required fields? Renamed fields? `fp8_recipe`
 356 | type changed?
 357 | 
 358 | #### `get_megatron_optimizer(config, model_chunks)`
 359 | 
 360 | Called in `megatron_engine.py:980`:
 361 | 
 362 | ```python
 363 | self.optimizer = get_megatron_optimizer(mcore_opt_config, self.model)
 364 | ```
 365 | 
 366 | **Check:** Signature change — does it still accept `(config, model_chunks)`? Any new
 367 | required params (e.g., `model_parallel_config`)? Return type interface: `.step()` should
 368 | return `(update_successful, grad_norm, num_zeros)`, `.param_groups`, `.zero_grad()`,
 369 | `.get_loss_scale()`, `.sharded_state_dict(state_dict)`, `.load_state_dict(state_dict)`.
 370 | 
 371 | ______________________________________________________________________
 372 | 
 373 | ### 5. `megatron.core.optimizer_param_scheduler`
 374 | 
 375 | **Source:** `Megatron-LM/megatron/core/optimizer_param_scheduler.py`
 376 | 
 377 | #### `OptimizerParamScheduler`
 378 | 
 379 | Constructed in `megatron_engine.py:987`:
 380 | 
 381 | ```python
 382 | OptimizerParamScheduler(
 383 |     optimizer, init_lr=..., max_lr=..., min_lr=...,
 384 |     lr_warmup_steps=..., lr_decay_steps=..., lr_decay_style=...,
 385 |     start_wd=..., end_wd=..., wd_incr_steps=..., wd_incr_style="constant",
 386 | )
 387 | ```
 388 | 
 389 | Methods used: `.step(1)`, `.state_dict()`, `.load_state_dict(state_dict)`.
 390 | 
 391 | **Check:** Constructor params — any renamed or removed? New required params? `.step()`
 392 | accepts integer increment?
 393 | 
 394 | ______________________________________________________________________
 395 | 
 396 | ### 6. `megatron.core.pipeline_parallel`
 397 | 
 398 | **Source:** `Megatron-LM/megatron/core/pipeline_parallel/`
 399 | 
 400 | #### `get_forward_backward_func()`
 401 | 
 402 | Called in `megatron_engine.py:621`. Returns a callable invoked as:
 403 | 
 404 | ```python
 405 | forward_backward_func(
 406 |     forward_step_func=forward_step,
 407 |     data_iterator=data_iterator,
 408 |     model=...,
 409 |     num_microbatches=...,
 410 |     seq_length=...,
 411 |     micro_batch_size=...,
 412 |     forward_only=...,
 413 | )
 414 | ```
 415 | 
 416 | **Check:** Return type callable signature. `forward_step_func` expected signature:
 417 | `(batch_iter, model) -> (output, loss_func)`. Any new required params like
 418 | `collect_non_loss_data`, `first_val_step`, `config`?
 419 | 
 420 | ______________________________________________________________________
 421 | 
 422 | ### 7. `megatron.core.transformer`
 423 | 
 424 | **Source:** `Megatron-LM/megatron/core/transformer/`
 425 | 
 426 | #### `TransformerConfig`
 427 | 
 428 | Used everywhere as configuration dataclass. Created via `bridge.config` or explicitly in
 429 | `common.py:check_and_construct_configs`.
 430 | 
 431 | Fields accessed in AReaL code:
 432 | 
 433 | - `hidden_size`, `num_attention_heads`, `num_query_groups`, `kv_channels`
 434 | - `ffn_hidden_size`, `num_layers`
 435 | - `num_moe_experts`, `moe_ffn_hidden_size`, `moe_layer_freq`
 436 | - `moe_shared_expert_intermediate_size`, `moe_router_enable_expert_bias`
 437 | - `expert_model_parallel_size`
 438 | - `sequence_parallel`, `context_parallel_size`
 439 | - `params_dtype`, `pipeline_dtype`, `bf16`, `fp16`
 440 | - `fp8`, `fp8_param`, `fp8_recipe`, and other `fp8_*` fields
 441 | - `gated_linear_unit`, `add_bias_linear`
 442 | - `deterministic_mode`, `cross_entropy_loss_fusion`, `bias_dropout_fusion`
 443 | - `no_sync_func`, `param_sync_func`, `finalize_model_grads_func`
 444 | - `variable_seq_lengths`, `masked_softmax_fusion`
 445 | - `pipeline_model_parallel_layout`
 446 | - `num_layers_in_first_pipeline_stage`, `num_layers_in_last_pipeline_stage`
 447 | - `account_for_embedding_in_pipeline_split`, `account_for_loss_in_pipeline_split`
 448 | 
 449 | **Check:** `check_and_construct_configs()` in `common.py` already handles removed fields
 450 | gracefully. But verify new required fields that may not have defaults.
 451 | 
 452 | #### `TransformerBlockSubmodules`, `TransformerLayer`, `TransformerLayerSubmodules`
 453 | 
 454 | Used in `module_megatron.py` for tree attention patching. Accessed via:
 455 | 
 456 | ```python
 457 | spec.layer_specs  # list of layer specs
 458 | layer_spec.module  # should be TransformerLayer
 459 | layer_spec.submodules  # TransformerLayerSubmodules
 460 | submodules.self_attention  # attention spec
 461 | self_attn_spec.module  # should be SelfAttention
 462 | self_attn_spec.params["attn_mask_type"] = AttnMaskType.arbitrary
 463 | self_attn_spec.submodules.core_attention = PytorchFlexAttention
 464 | ```
 465 | 
 466 | **Check:** `.layer_specs`, `.submodules`, `.self_attention`, `.params`,
 467 | `.submodules.core_attention` still exist on these objects?
 468 | 
 469 | #### `SelfAttention`
 470 | 
 471 | Used as a class reference check in `module_megatron.py:203`. Not instantiated directly.
 472 | 
 473 | **Check:** Still exists at `megatron.core.transformer.attention.SelfAttention`?
 474 | 
 475 | #### `AttnMaskType`
 476 | 
 477 | Used: `AttnMaskType.arbitrary` in `module_megatron.py:206`.
 478 | 
 479 | **Check:** `.arbitrary` enum value still exists?
 480 | 
 481 | #### `get_transformer_layer_offset(config, vp_stage=)`
 482 | 
 483 | Called in `megatron.py:612`:
 484 | 
 485 | ```python
 486 | layer_offset = get_transformer_layer_offset(config, vp_stage=vp_stage)
 487 | ```
 488 | 
 489 | **Check:** Signature.
 490 | 
 491 | #### `PipelineParallelLayerLayout`
 492 | 
 493 | Constructed in `pipeline_parallel.py:62`:
 494 | 
 495 | ```python
 496 | PipelineParallelLayerLayout(layout=layout, pipeline_model_parallel_size=pp_size)
 497 | ```
 498 | 
 499 | **Check:** Constructor params.
 500 | 
 501 | ______________________________________________________________________
 502 | 
 503 | ### 8. `megatron.core.models.gpt`
 504 | 
 505 | **Source:** `Megatron-LM/megatron/core/models/gpt/`
 506 | 
 507 | #### `GPTModel`
 508 | 
 509 | Constructed in `registry.py:179`:
 510 | 
 511 | ```python
 512 | GPTModel(
 513 |     config=tf_config, transformer_layer_spec=..., vocab_size=...,
 514 |     max_sequence_length=..., pre_process=True, post_process=True,
 515 |     share_embeddings_and_output_weights=False,
 516 |     position_embedding_type="rope", rotary_base=...,
 517 | )
 518 | ```
 519 | 
 520 | Attributes/methods used: `.output_layer`, `.vocab_size`, `.sharded_state_dict()`,
 521 | `.config`, `.module`, `.named_parameters()`, `.load_state_dict()`, `.state_dict()`.
 522 | 
 523 | **Check:** Constructor signature. `position_embedding_type` values. New required params?
 524 | 
 525 | #### `get_gpt_decoder_block_spec(config, use_transformer_engine=True)`
 526 | 
 527 | Called in `qwen3.py:32`:
 528 | 
 529 | ```python
 530 | get_gpt_decoder_block_spec(tfconfig, use_transformer_engine=use_te)
 531 | ```
 532 | 
 533 | **Check:** Signature. Was it renamed? Does it accept the same args?
 534 | 
 535 | ______________________________________________________________________
 536 | 
 537 | ### 9. `megatron.core.fp8_utils`
 538 | 
 539 | **Source:** `Megatron-LM/megatron/core/fp8_utils.py`
 540 | 
 541 | #### `is_float8tensor(param)`
 542 | 
 543 | Called in `megatron.py:83`, `tensor_helper.py:4`, `hf_load.py:12`, `hf_save.py:13`,
 544 | `test_fp8_rmsnorm.py:15`.
 545 | 
 546 | **Check:** Still exists? Signature unchanged?
 547 | 
 548 | #### `get_fp8_context()`
 549 | 
 550 | Called in `test_fp8_rmsnorm.py:15`.
 551 | 
 552 | **Check:** Signature.
 553 | 
 554 | ______________________________________________________________________
 555 | 
 556 | ### 10. `megatron.core.dist_checkpointing`
 557 | 
 558 | **Source:** `Megatron-LM/megatron/core/dist_checkpointing/`
 559 | 
 560 | #### `dist_checkpointing.save(...)`
 561 | 
 562 | Called in `checkpointer.py:60`:
 563 | 
 564 | ```python
 565 | dist_checkpointing.save(
 566 |     sharded_state_dict, ckpt_path,
 567 |     sharded_strategy=save_strategy,
 568 |     async_sharded_save=async_save,
 569 |     validate_access_integrity=validate_sharding_integrity,
 570 | )
 571 | ```
 572 | 
 573 | **Check:** `async_sharded_save` renamed? `validate_access_integrity` still exists?
 574 | 
 575 | #### `dist_checkpointing.load(...)`
 576 | 
 577 | Called in `checkpointer.py:79`:
 578 | 
 579 | ```python
 580 | dist_checkpointing.load(sharded_state_dict, ckpt_dir, sharded_strategy=load_strategy)
 581 | ```
 582 | 
 583 | **Check:** Signature.
 584 | 
 585 | #### `ShardedObject(key, data, global_shape, global_offset, replica_id=)`
 586 | 
 587 | Called in `checkpointer.py:198`.
 588 | 
 589 | **Check:** Constructor params.
 590 | 
 591 | #### Serialization strategies
 592 | 
 593 | ```python
 594 | get_default_load_sharded_strategy(ckpt_dir)
 595 | get_default_save_sharded_strategy("torch_dist")
 596 | FullyParallelLoadStrategyWrapper(load_strategy, group)
 597 | FullyParallelSaveStrategyWrapper(save_strategy, group)
 598 | ```
 599 | 
 600 | **Check:** All four still exist? Signatures unchanged?
 601 | 
 602 | ______________________________________________________________________
 603 | 
 604 | ### 11. `megatron.core.packed_seq_params`
 605 | 
 606 | **Source:** `Megatron-LM/megatron/core/packed_seq_params.py`
 607 | 
 608 | #### `PackedSeqParams`
 609 | 
 610 | Constructed in `packed_context_parallel.py:34`:
 611 | 
 612 | ```python
 613 | PackedSeqParams(
 614 |     qkv_format="thd",
 615 |     cu_seqlens_q=cu_seqlens, max_seqlen_q=max_seqlen,
 616 |     cu_seqlens_kv=cu_seqlens, max_seqlen_kv=max_seqlen,
 617 |     cu_seqlens_q_padded=cu_seqlens, cu_seqlens_kv_padded=cu_seqlens,
 618 | )
 619 | ```
 620 | 
 621 | **Check:** Constructor fields.
 622 | 
 623 | ______________________________________________________________________
 624 | 
 625 | ### 12. `megatron.core.utils`
 626 | 
 627 | **Source:** `Megatron-LM/megatron/core/utils.py`
 628 | 
 629 | #### `get_model_config(model)`
 630 | 
 631 | Called in `megatron_engine.py:326`, `test_fp8_rmsnorm.py:16`.
 632 | 
 633 | **Check:** Signature. Return type. What fields are expected on the returned config
 634 | object (`.no_sync_func`, `.param_sync_func`, `.finalize_model_grads_func`,
 635 | `.deterministic_mode`, `.cross_entropy_loss_fusion`, `.bias_dropout_fusion`)?
 636 | 
 637 | ______________________________________________________________________
 638 | 
 639 | ## Upgrade Workflow
 640 | 
 641 | ### Step 0: Prepare Megatron-LM source
 642 | 
 643 | Clone or checkout the target version as described in Prerequisites above.
 644 | 
 645 | ### Step 1: Audit `megatron.core` API signatures
 646 | 
 647 | For EACH entry in the API Usage Catalog above:
 648 | 
 649 | 1. Open the upstream source file at the target version.
 650 | 1. Compare the function/class signature against the current AReaL invocation.
 651 | 1. Flag any of:
 652 |    - **Removed parameters** still passed by AReaL → must remove from call site
 653 |    - **Renamed parameters** → must rename in call site
 654 |    - **New required parameters** (no default) → must add to call site
 655 |    - **New optional parameters** with useful defaults → document but skip
 656 |    - **Changed return types** → must update consumers
 657 |    - **Removed functions/classes** → must find replacement
 658 |    - **Changed method signatures** on returned objects → must update call sites
 659 | 1. Record findings per-file.
 660 | 
 661 | ### Step 2: Audit `mbridge` compatibility
 662 | 
 663 | mbridge wraps megatron.core and may also need updates. Cross-reference the cloned
 664 | `mbridge-src/` repo to verify each API AReaL depends on.
 665 | 
 666 | #### 2a. Public API (used directly by AReaL)
 667 | 
 668 | | AReaL Call Site                     | mbridge API                                                                           | Source File to Check                                                                                      |
 669 | | ----------------------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
 670 | | `megatron_engine.py:242`            | `AutoBridge.from_pretrained(path)`                                                    | `mbridge-src/mbridge/core/auto_bridge.py` — `from_pretrained()` resolves model type via `_MODEL_REGISTRY` |
 671 | | `registry.py:139`                   | `bridge.get_model(wrap_with_ddp=..., ddp_config=..., use_torch_fsdp2=..., ...)`       | `mbridge-src/mbridge/core/bridge.py` — `get_model()` passes kwargs to `get_model()` util                  |
 672 | | `megatron_engine.py`                | `bridge.load_weights(model, path)`                                                    | `mbridge-src/mbridge/core/bridge.py` — `load_weights()`                                                   |
 673 | | `megatron_engine.py`                | `bridge.save_weights(models, path, memory_efficient=..., distributed_filesystem=...)` | `mbridge-src/mbridge/core/bridge.py` — `save_weights()` and `_save_weights_fast()`                        |
 674 | | `megatron_engine.py`                | `bridge.export_weights(models)`                                                       | `mbridge-src/mbridge/core/bridge.py` — `export_weights()` generator                                       |
 675 | | `megatron_engine.py`                | `bridge.set_extra_args(**kwargs)`                                                     | `mbridge-src/mbridge/core/bridge.py` — rebuilds `self.config`                                             |
 676 | | `registry.py`, `megatron_engine.py` | `bridge.config` (returns `TransformerConfig`)                                         | `mbridge-src/mbridge/core/llm_bridge.py` — `_build_base_config()` constructs the config                   |
 677 | | `registry.py`, `hf_save.py`         | `bridge.hf_config`                                                                    | Stored on `Bridge.__init__()` from HF `AutoConfig`                                                        |
 678 | 
 679 | **Check:** Do `get_model()` kwargs still match `bridge.py:get_model()` signature? Does
 680 | `_build_base_config()` in `llm_bridge.py` pass any new required fields to
 681 | `TransformerConfig`? Does `set_extra_args()` still call `_build_config()`?
 682 | 
 683 | #### 2b. Private/internal API (used by AReaL's custom weight loaders)
 684 | 
 685 | | AReaL Call Site  | mbridge Private API                                                           | Source File to Check                                                                            |
 686 | | ---------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
 687 | | `hf_load.py:396` | `bridge._weight_name_mapping_mcore_local_to_global(model)`                    | `mbridge-src/mbridge/core/bridge.py` — maps VPP+EP local names to global                        |
 688 | | `hf_load.py:399` | `bridge._weight_name_mapping_mcore_to_hf(global_name)`                        | `mbridge-src/mbridge/core/bridge.py` — dispatches to `_weight_name_mapping_attention/mlp/other` |
 689 | | `hf_save.py:376` | `bridge._weight_to_hf_format(global_name, infer_params)`                      | `mbridge-src/mbridge/core/bridge.py` — splits QKV/gate-up, returns `(names, tensors)`           |
 690 | | `hf_save.py:368` | `bridge._weight_merge_across_tp(name, params, param)`                         | `mbridge-src/mbridge/core/bridge.py` — merges TP-split tensors                                  |
 691 | | `hf_load.py:365` | `bridge._get_actual_hf_path(weights_path)`                                    | `mbridge-src/mbridge/core/bridge.py` or subclass — resolves HF cache paths                      |
 692 | | `hf_save.py:197` | `bridge._weight_name_mapping_mcore_local_to_global(model, consider_ep=False)` | Same as above but with `consider_ep` kwarg                                                      |
 693 | | `hf_save.py:452` | `bridge.config.num_moe_experts`                                               | Field on `TransformerConfig` built by `_build_base_config()`                                    |
 694 | | `hf_save.py:536` | `bridge.hf_config.save_pretrained(weights_path)`                              | Standard HF `PretrainedConfig` method                                                           |
 695 | | `hf_save.py:191` | `unwrap_model(model)` from `mbridge.core.util`                                | `mbridge-src/mbridge/core/util.py` — unwraps DDP/Float16Module/FSDP wrappers                    |
 696 | 
 697 | **Check:** Do any of these private methods have changed signatures? Has the weight name
 698 | mapping logic changed (e.g., new `_DIRECT_MAPPING`, `_ATTENTION_MAPPING`, or
 699 | `_MLP_MAPPING` entries)? Does `unwrap_model()` still handle the same wrapper classes?
 700 | 
 701 | #### 2c. `LLMBridge._get_transformer_layer_spec()` (monkey-patched by tree attention)
 702 | 
 703 | | AReaL Call Site              | mbridge API                                             | Source File to Check                                                            |
 704 | | ---------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------- |
 705 | | `module_megatron.py:193,211` | `LLMBridge._get_transformer_layer_spec(self, vp_stage)` | `mbridge-src/mbridge/core/llm_bridge.py` — calls `get_gpt_decoder_block_spec()` |
 706 | 
 707 | AReaL monkey-patches this method to inject `PytorchFlexAttention` as `core_attention`.
 708 | The patch accesses `spec.layer_specs[i].submodules.self_attention.params` and
 709 | `spec.layer_specs[i].submodules.self_attention.submodules.core_attention`.
 710 | 
 711 | **Check:** Does `_get_transformer_layer_spec()` still return a
 712 | `TransformerBlockSubmodules` with `.layer_specs` list? Does each layer spec still have
 713 | `.submodules.self_attention.params` dict and `.submodules.core_attention` attribute? Has
 714 | the `vp_stage` parameter been added/removed?
 715 | 
 716 | #### 2d. mbridge version compatibility
 717 | 
 718 | If mbridge also needs a version bump to work with the new megatron-core, note the
 719 | compatible mbridge version. Check `mbridge-src/pyproject.toml` for its megatron-core
 720 | version pin.
 721 | 
 722 | ### Step 3: Update `pyproject.toml`
 723 | 
 724 | Update the `megatron-core` (and optionally `mbridge`) version pin in `pyproject.toml`.
 725 | Run `uv lock` to verify dependency resolution.
 726 | 
 727 | ### Step 4: Apply code changes
 728 | 
 729 | For each flagged incompatibility from Steps 1-2:
 730 | 
 731 | 1. Update the call site in the affected file.
 732 | 1. Preserve existing behavior — do NOT refactor beyond what's required.
 733 | 1. If a function was removed, check the upstream migration guide or changelog.
 734 | 1. If a mbridge API changed (Step 2b/2c), update AReaL's usage to match the new mbridge
 735 |    signatures. Common cases:
 736 |    - `bridge.get_model()` gained/lost kwargs → update `registry.py:139`
 737 |    - `bridge._weight_*` private methods renamed or re-signed → update `hf_load.py` and
 738 |      `hf_save.py` callers
 739 |    - `LLMBridge._get_transformer_layer_spec()` return structure changed → update the
 740 |      monkey-patch in `module_megatron.py`
 741 |    - `unwrap_model()` wrapper class list changed → verify unwrapping still works
 742 | 
 743 | Priority order for applying changes:
 744 | 
 745 | 1. `areal/engine/megatron_engine.py` (highest risk, most API surface)
 746 | 1. `areal/engine/megatron_utils/megatron.py`
 747 | 1. `areal/engine/megatron_utils/checkpointer.py`
 748 | 1. `areal/engine/megatron_utils/packed_context_parallel.py`
 749 | 1. `areal/engine/megatron_utils/pipeline_parallel.py`
 750 | 1. `areal/engine/megatron_utils/fp8/tensor_helper.py`
 751 | 1. `areal/models/mcore/registry.py`
 752 | 1. `areal/models/mcore/common.py`
 753 | 1. `areal/models/mcore/qwen3.py`
 754 | 1. `areal/models/mcore/hf_load.py` (mbridge private API consumer)
 755 | 1. `areal/models/mcore/hf_save.py` (mbridge private API consumer)
 756 | 1. `areal/models/tree_attn/module_megatron.py` (mbridge monkey-patch)
 757 | 1. Test files
 758 | 
 759 | ### Step 5: Verify `TransformerConfig` field compatibility
 760 | 
 761 | `areal/models/mcore/common.py` uses `check_and_construct_configs()` which automatically
 762 | removes unsupported fields. However:
 763 | 
 764 | 1. Check that no **new required fields** (without defaults) were added to
 765 |    `TransformerConfig`.
 766 | 1. Verify `hf_to_mcore_base_args()` in `common.py` — the hardcoded field names
 767 |    (`num_layers`, `hidden_size`, etc.) still match.
 768 | 1. Check if `FP8`-related fields on `TransformerConfig` changed (used in
 769 |    `megatron_engine.py:_check_and_apply_fp8_config()`).
 770 | 
 771 | ### Step 6: Run pre-commit and tests
 772 | 
 773 | ```bash
 774 | pre-commit run --all-files
 775 | uv run pytest tests/test_estimate_num_params.py -v
 776 | ```
 777 | 
 778 | If GPU is available:
 779 | 
 780 | ```bash
 781 | uv run pytest tests/fp8/ -v
 782 | ```
 783 | 
 784 | ### Step 7: Report changes
 785 | 
 786 | Output a summary in this format:
 787 | 
 788 | ```
 789 | ## Upgrade Summary: megatron-core ${OLD_VERSION} → ${NEW_VERSION}
 790 | 
 791 | ### Breaking Changes Found
 792 | - [file:line] description of change needed
 793 | 
 794 | ### mbridge Compatibility
 795 | - mbridge version: ${MBRIDGE_VERSION} (compatible / needs bump to X.Y.Z)
 796 | - mbridge API changes affecting AReaL: (list or "none")
 797 | 
 798 | ### API Additions (new optional params, informational)
 799 | - [upstream_file] description
 800 | 
 801 | ### Files Modified
 802 | - path/to/file.py: description of change
 803 | 
 804 | ### Tests
 805 | - ✅ pre-commit passed
 806 | - ✅ test_estimate_num_params passed
 807 | - ⬚ FP8 tests (requires GPU)
 808 | ```
 809 | 
 810 | If there are unresolvable breaking changes, STOP and ask the user before proceeding.
```


---
## .claude/commands/upgrade-vllm.md

```
   1 | ---
   2 | name: upgrade-vllm
   3 | description: Upgrade vLLM version in AReaL. Audits all vLLM API usage, cross-references upstream source, and updates call sites for compatibility.
   4 | argument-hint: <version>
   5 | ---
   6 | 
   7 | ## Usage
   8 | 
   9 | ```
  10 | /upgrade-vllm $ARGUMENTS
  11 | ```
  12 | 
  13 | **Arguments (`$VERSION`):** Target vLLM version tag or commit hash, e.g. `v0.18.0`,
  14 | `0.17.0`, or a commit SHA. If not given, get the required version from AReaL's
  15 | "pyproject.toml" and check whether the current code is fully compatible with the
  16 | specified version.
  17 | 
  18 | ## Prerequisites — Source Code for Cross-Referencing
  19 | 
  20 | This command requires the upstream vLLM source repo to cross-reference API signatures.
  21 | 
  22 | ### vLLM
  23 | 
  24 | ```bash
  25 | VLLM_DIR="${REPO_ROOT}/vllm-src"
  26 | # Validate VERSION to prevent command injection
  27 | if [[ ! "$VERSION" =~ ^[a-zA-Z0-9._/-]+$ ]]; then
  28 |   echo "Error: Invalid version format: $VERSION"
  29 |   exit 1
  30 | fi
  31 | if [ ! -d "$VLLM_DIR" ]; then
  32 |   git clone --depth 1 --branch "${VERSION}" https://github.com/vllm-project/vllm.git "$VLLM_DIR"
  33 | else
  34 |   cd "$VLLM_DIR" && git fetch origin && git checkout "${VERSION}" && cd -
  35 | fi
  36 | ```
  37 | 
  38 | If cloning or checkout fails, report to the user immediately.
  39 | 
  40 | The relevant upstream source paths are:
  41 | 
  42 | - `vllm-src/vllm/entrypoints/openai/api_server.py`
  43 | - `vllm-src/vllm/entrypoints/openai/cli_args.py`
  44 | - `vllm-src/vllm/entrypoints/openai/completion/api_router.py`
  45 | - `vllm-src/vllm/entrypoints/openai/completion/protocol.py`
  46 | - `vllm-src/vllm/entrypoints/openai/engine/protocol.py`
  47 | - `vllm-src/vllm/entrypoints/openai/utils.py`
  48 | - `vllm-src/vllm/entrypoints/utils.py`
  49 | - `vllm-src/vllm/logger.py`
  50 | - `vllm-src/vllm/lora/request.py`
  51 | - `vllm-src/vllm/utils/argparse_utils.py`
  52 | - `vllm-src/vllm/v1/engine/__init__.py`
  53 | - `vllm-src/vllm/v1/engine/core.py`
  54 | - `vllm-src/vllm/v1/engine/output_processor.py`
  55 | - `vllm-src/vllm/v1/metrics/stats.py`
  56 | - `vllm-src/vllm/v1/request.py`
  57 | - `vllm-src/vllm/v1/worker/gpu_worker.py`
  58 | - `vllm-src/vllm/worker/worker.py`
  59 | - `vllm-src/vllm/lora/lora_model.py`
  60 | - `vllm-src/vllm/lora/peft_helper.py`
  61 | - `vllm-src/vllm/model_executor/model_loader/__init__.py`
  62 | - `vllm-src/vllm/envs.py`
  63 | 
  64 | ______________________________________________________________________
  65 | 
  66 | ## Affected Files
  67 | 
  68 | ### Primary (engine layer — most likely to break)
  69 | 
  70 | | File                                             | Imports / Usage                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
  71 | | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  72 | | `areal/engine/vllm_ext/areal_vllm_server.py`     | `entrypoints.openai.api_server` (`build_app`, `run_server`), `entrypoints.openai.cli_args`, `entrypoints.openai.completion.api_router` (`create_completion`), `entrypoints.openai.completion.protocol` (`CompletionRequest`), `entrypoints.openai.engine.protocol` (`ErrorResponse`, `OpenAIBaseModel`), `entrypoints.openai.utils` (`validate_json_request`), `entrypoints.utils`, `logger`, `lora.request`, `utils.argparse_utils`, `v1.engine`, `v1.engine.core`, `v1.metrics.stats`, `v1.request`, `v1.engine.output_processor` |
  73 | | `areal/engine/vllm_ext/vllm_worker_extension.py` | `logger`, `lora.lora_model`, `lora.peft_helper`, `lora.request`, `model_executor.model_loader`                                                                                                                                                                                                                                                                                                                                                                                                                                      |
  74 | | `areal/engine/vllm_remote.py`                    | `VLLMBackend` class (builds HTTP requests to vLLM endpoints), `RemotevLLMEngine` wrapper                                                                                                                                                                                                                                                                                                                                                                                                                                            |
  75 | 
  76 | ### Secondary (infrastructure / platform layer)
  77 | 
  78 | | File                                  | Imports / Usage                                                                                            |
  79 | | ------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
  80 | | `areal/infra/platforms/cuda.py`       | `vllm.v1.worker.gpu_worker.Worker` (try), `vllm.worker.worker.Worker` (fallback) via try/except            |
  81 | | `areal/infra/platforms/unknown.py`    | Same as `cuda.py`                                                                                          |
  82 | | `areal/infra/platforms/platform.py`   | Abstract `get_vllm_worker_class()` method                                                                  |
  83 | | `areal/infra/launcher/vllm_server.py` | `vLLMServerWrapper`, `launch_server_cmd`, env vars (`VLLM_CACHE_ROOT`, `VLLM_ALLOW_RUNTIME_LORA_UPDATING`) |
  84 | | `areal/infra/launcher/ray.py`         | vLLM server launch in Ray cluster (imports `vLLMConfig`)                                                   |
  85 | | `areal/infra/launcher/local.py`       | vLLM server launch locally (imports `vLLMConfig`)                                                          |
  86 | | `areal/infra/launcher/slurm.py`       | vLLM server launch in Slurm (imports `vLLMConfig`)                                                         |
  87 | | `areal/infra/launcher/__init__.py`    | Re-exports `launch_vllm_server`, `vLLMServerWrapper`                                                       |
  88 | | `areal/infra/utils/launcher.py`       | `VLLM_CACHE_ROOT` path, vLLM allocation mode validation                                                    |
  89 | 
  90 | ### Tertiary (config / API / workflow layer)
  91 | 
  92 | | File                                          | Usage                                                            |
  93 | | --------------------------------------------- | ---------------------------------------------------------------- |
  94 | | `areal/api/cli_args.py`                       | `vLLMConfig` dataclass — all vLLM CLI flags and server arguments |
  95 | | `areal/api/alloc_mode.py`                     | `"vllm"` as a backend literal type                               |
  96 | | `areal/api/io_struct.py`                      | `vision_msg_vllm` field on `ModelRequest`                        |
  97 | | `areal/trainer/rl_trainer.py`                 | `RemotevLLMEngine` initialization, `vLLMConfig.build_args()`     |
  98 | | `areal/workflow/vision_rlvr.py`               | Sets `vision_msg_vllm` on `ModelRequest`                         |
  99 | | `areal/tools/validate_docker_installation.py` | Checks `vllm` is importable, validates `vllm._C`                 |
 100 | | `areal/tools/validation_base.py`              | `vllm._C` as native extension verification                       |
 101 | 
 102 | ### Test files
 103 | 
 104 | | File                              | Usage                                                      |
 105 | | --------------------------------- | ---------------------------------------------------------- |
 106 | | `tests/test_inference_engines.py` | `vLLMConfig`, `RemotevLLMEngine`, engine integration tests |
 107 | | `tests/test_model_utils.py`       | vLLM allocation mode regression tests                      |
 108 | | `tests/test_allocation_mode.py`   | vLLM allocation mode parsing tests                         |
 109 | | `tests/test_examples.py`          | vLLM integration test configurations                       |
 110 | | `tests/grpo/test_grpo.py`         | vLLM references in GRPO config tests                       |
 111 | 
 112 | ______________________________________________________________________
 113 | 
 114 | ## API Usage Catalog
 115 | 
 116 | For each function/class below, verify the call signature against the upstream source at
 117 | the target version. Focus on: **missing new required parameters**, **removed old
 118 | parameters**, **renamed parameters**, **changed return types**, **changed method
 119 | signatures on returned objects**, and **moved/renamed modules**.
 120 | 
 121 | ### 1. `vllm.entrypoints.openai.api_server`
 122 | 
 123 | **Source:** `vllm-src/vllm/entrypoints/openai/api_server.py`
 124 | 
 125 | #### `build_app(args, supported_tasks=None)`
 126 | 
 127 | Imported in `areal_vllm_server.py:9` as `_original_build_app`:
 128 | 
 129 | ```python
 130 | from vllm.entrypoints.openai.api_server import build_app as _original_build_app
 131 | ```
 132 | 
 133 | AReaL monkey-patches `build_app` to inject custom routes in
 134 | `areal_vllm_server.py:458-480`:
 135 | 
 136 | ```python
 137 | import vllm.entrypoints.openai.api_server as _api_server_module
 138 | 
 139 | def _areal_build_app(args, supported_tasks=None):
 140 |     app = _original_build_app(args, supported_tasks=supported_tasks)
 141 |     # Remove vLLM's /v1/completions POST route so AReaL's takes precedence
 142 |     app.router.routes = [
 143 |         route for route in app.router.routes
 144 |         if not (hasattr(route, "path") and route.path == "/v1/completions"
 145 |                 and hasattr(route, "methods") and "POST" in route.methods)
 146 |     ]
 147 |     app.include_router(router)
 148 |     return app
 149 | 
 150 | _api_server_module.build_app = _areal_build_app
 151 | ```
 152 | 
 153 | **Check:** Does `build_app` still exist? Still accepts `(args, supported_tasks=None)`?
 154 | Does it return a FastAPI app? Does the returned app still have `router.routes` with
 155 | `path` and `methods` attributes on route objects?
 156 | 
 157 | #### `run_server(args)`
 158 | 
 159 | Imported in `areal_vllm_server.py:10`:
 160 | 
 161 | ```python
 162 | from vllm.entrypoints.openai.api_server import run_server
 163 | ```
 164 | 
 165 | Called in `areal_vllm_server.py:490`:
 166 | 
 167 | ```python
 168 | uvloop.run(run_server(args))
 169 | ```
 170 | 
 171 | **Check:** Signature. Is it still async? Does it still accept parsed args directly? Does
 172 | it internally call `build_app` (which AReaL monkey-patches)?
 173 | 
 174 | ______________________________________________________________________
 175 | 
 176 | ### 2. `vllm.entrypoints.openai.cli_args`
 177 | 
 178 | **Source:** `vllm-src/vllm/entrypoints/openai/cli_args.py`
 179 | 
 180 | #### `make_arg_parser(parser)`
 181 | 
 182 | Called in `areal_vllm_server.py:486`:
 183 | 
 184 | ```python
 185 | parser = make_arg_parser(parser)
 186 | ```
 187 | 
 188 | **Check:** Signature. Does it still accept a parser and return a parser? New required
 189 | args?
 190 | 
 191 | #### `validate_parsed_serve_args(args)`
 192 | 
 193 | Called in `areal_vllm_server.py:488`:
 194 | 
 195 | ```python
 196 | validate_parsed_serve_args(args)
 197 | ```
 198 | 
 199 | **Check:** Signature. Still exists?
 200 | 
 201 | ______________________________________________________________________
 202 | 
 203 | ### 3. `vllm.entrypoints.openai.completion.api_router`
 204 | 
 205 | **Source:** `vllm-src/vllm/entrypoints/openai/completion/api_router.py`
 206 | 
 207 | #### `create_completion` (aliased as `original_create_completion`)
 208 | 
 209 | Imported in `areal_vllm_server.py:12-14`:
 210 | 
 211 | ```python
 212 | from vllm.entrypoints.openai.completion.api_router import (
 213 |     create_completion as original_create_completion,
 214 | )
 215 | ```
 216 | 
 217 | Called in `areal_vllm_server.py:333`:
 218 | 
 219 | ```python
 220 | response = await original_create_completion(request, raw_request)
 221 | ```
 222 | 
 223 | **Check:** Signature `(request: CompletionRequest, raw_request: Request)` still valid?
 224 | Was this function moved or renamed? Is the module path still
 225 | `vllm.entrypoints.openai.completion.api_router`?
 226 | 
 227 | ______________________________________________________________________
 228 | 
 229 | ### 4. `vllm.entrypoints.openai.completion.protocol`
 230 | 
 231 | **Source:** `vllm-src/vllm/entrypoints/openai/completion/protocol.py`
 232 | 
 233 | #### `CompletionRequest`
 234 | 
 235 | Imported in `areal_vllm_server.py:15`:
 236 | 
 237 | ```python
 238 | from vllm.entrypoints.openai.completion.protocol import CompletionRequest
 239 | ```
 240 | 
 241 | Used as type annotation in `areal_vllm_server.py:327`:
 242 | 
 243 | ```python
 244 | async def create_completion(request: CompletionRequest, raw_request: Request):
 245 | ```
 246 | 
 247 | **Check:** Still exists at this module path? Fields unchanged? Was this class moved?
 248 | 
 249 | ______________________________________________________________________
 250 | 
 251 | ### 5. `vllm.entrypoints.openai.engine.protocol`
 252 | 
 253 | **Source:** `vllm-src/vllm/entrypoints/openai/engine/protocol.py`
 254 | 
 255 | #### `ErrorResponse`
 256 | 
 257 | Imported in `areal_vllm_server.py:16`:
 258 | 
 259 | ```python
 260 | from vllm.entrypoints.openai.engine.protocol import ErrorResponse, OpenAIBaseModel
 261 | ```
 262 | 
 263 | Used in route response model in `areal_vllm_server.py:320-322`:
 264 | 
 265 | ```python
 266 | HTTPStatus.BAD_REQUEST.value: {"model": ErrorResponse},
 267 | HTTPStatus.NOT_FOUND.value: {"model": ErrorResponse},
 268 | HTTPStatus.INTERNAL_SERVER_ERROR.value: {"model": ErrorResponse},
 269 | ```
 270 | 
 271 | **Check:** Still exists at this module path?
 272 | 
 273 | #### `OpenAIBaseModel`
 274 | 
 275 | AReaL request classes inherit from it in `areal_vllm_server.py:41-92`:
 276 | 
 277 | ```python
 278 | class UpdateWeightsRequest(OpenAIBaseModel):
 279 |     model_path: str
 280 |     ...
 281 | ```
 282 | 
 283 | **Check:** Still exists? Still a Pydantic model base class? Was it moved?
 284 | 
 285 | ______________________________________________________________________
 286 | 
 287 | ### 6. `vllm.entrypoints.openai.utils`
 288 | 
 289 | **Source:** `vllm-src/vllm/entrypoints/openai/utils.py`
 290 | 
 291 | #### `validate_json_request`
 292 | 
 293 | Imported in `areal_vllm_server.py:17`:
 294 | 
 295 | ```python
 296 | from vllm.entrypoints.openai.utils import validate_json_request
 297 | ```
 298 | 
 299 | Used as a FastAPI dependency in `areal_vllm_server.py:317`:
 300 | 
 301 | ```python
 302 | @router.post("/v1/completions", dependencies=[Depends(validate_json_request)])
 303 | ```
 304 | 
 305 | **Check:** Still exists at this module path? Still usable as a `Depends()` target?
 306 | 
 307 | ______________________________________________________________________
 308 | 
 309 | ### 7. `vllm.entrypoints.utils`
 310 | 
 311 | **Source:** `vllm-src/vllm/entrypoints/utils.py`
 312 | 
 313 | #### `cli_env_setup()`
 314 | 
 315 | Called in `areal_vllm_server.py:482`:
 316 | 
 317 | ```python
 318 | cli_env_setup()
 319 | ```
 320 | 
 321 | **Check:** Signature. Still exists?
 322 | 
 323 | #### `load_aware_call`
 324 | 
 325 | Used as decorator in `areal_vllm_server.py:326`:
 326 | 
 327 | ```python
 328 | @load_aware_call
 329 | async def create_completion(request: CompletionRequest, raw_request: Request):
 330 | ```
 331 | 
 332 | **Check:** Still a decorator? Signature?
 333 | 
 334 | #### `with_cancellation`
 335 | 
 336 | Used as decorator in `areal_vllm_server.py:325`:
 337 | 
 338 | ```python
 339 | @with_cancellation
 340 | @load_aware_call
 341 | async def create_completion(...):
 342 | ```
 343 | 
 344 | **Check:** Still a decorator? Order constraints?
 345 | 
 346 | ______________________________________________________________________
 347 | 
 348 | ### 8. `vllm.logger`
 349 | 
 350 | **Source:** `vllm-src/vllm/logger.py`
 351 | 
 352 | #### `init_logger(name)`
 353 | 
 354 | Called in `areal_vllm_server.py:33` and `vllm_worker_extension.py:15`:
 355 | 
 356 | ```python
 357 | logger = init_logger("areal_vllm_server")
 358 | logger = init_logger("vllm_worker_extension")
 359 | ```
 360 | 
 361 | **Check:** Signature unchanged?
 362 | 
 363 | ______________________________________________________________________
 364 | 
 365 | ### 9. `vllm.utils.argparse_utils`
 366 | 
 367 | **Source:** `vllm-src/vllm/utils/argparse_utils.py`
 368 | 
 369 | #### `FlexibleArgumentParser`
 370 | 
 371 | Used in `areal_vllm_server.py:483`:
 372 | 
 373 | ```python
 374 | parser = FlexibleArgumentParser(
 375 |     description="vLLM OpenAI-Compatible RESTful API server."
 376 | )
 377 | ```
 378 | 
 379 | **Check:** Still exists at this module path? Was it moved (e.g., to `vllm.utils`)?
 380 | 
 381 | ______________________________________________________________________
 382 | 
 383 | ### 10. `vllm.v1.engine` (V1 engine outputs)
 384 | 
 385 | **Source:** `vllm-src/vllm/v1/engine/__init__.py`
 386 | 
 387 | #### `EngineCoreOutput`
 388 | 
 389 | Constructed in `areal_vllm_server.py:355`:
 390 | 
 391 | ```python
 392 | EngineCoreOutput(
 393 |     request_id=req.request_id,
 394 |     new_token_ids=[],
 395 |     finish_reason=FinishReason.ABORT,
 396 |     new_logprobs=None,
 397 |     new_prompt_logprobs_tensors=None,
 398 |     stop_reason=None,
 399 | )
 400 | ```
 401 | 
 402 | **Check:** Constructor fields. New required fields? Field renames? Was
 403 | `new_prompt_logprobs_tensors` renamed? Was `stop_reason` removed?
 404 | 
 405 | #### `EngineCoreOutputs`
 406 | 
 407 | Constructed in `areal_vllm_server.py:371`:
 408 | 
 409 | ```python
 410 | EngineCoreOutputs(outputs=outputs)
 411 | ```
 412 | 
 413 | **Check:** Constructor signature. Still accepts `outputs` list?
 414 | 
 415 | #### `FinishReason`
 416 | 
 417 | Used in `areal_vllm_server.py:358`:
 418 | 
 419 | ```python
 420 | finish_reason=FinishReason.ABORT
 421 | ```
 422 | 
 423 | **Check:** `.ABORT` enum value still exists? Was `FinishReason` moved to a different
 424 | module?
 425 | 
 426 | ______________________________________________________________________
 427 | 
 428 | ### 11. `vllm.v1.engine.core`
 429 | 
 430 | **Source:** `vllm-src/vllm/v1/engine/core.py`
 431 | 
 432 | #### `EngineCore`
 433 | 
 434 | AReaL monkey-patches multiple methods onto this class in `areal_vllm_server.py:421-437`:
 435 | 
 436 | ```python
 437 | setattr(EngineCore, "abort_all_reqs", abort_all_reqs)
 438 | setattr(EngineCore, "areal_injected_update_weight", areal_injected_update_weight)
 439 | setattr(EngineCore, "areal_injected_update_weight_lora", areal_injected_update_weight_lora)
 440 | setattr(EngineCore, "areal_injected_update_weight_xccl", areal_injected_update_weight_xccl)
 441 | setattr(EngineCore, "areal_injected_update_weight_lora_xccl", areal_injected_update_weight_lora_xccl)
 442 | ```
 443 | 
 444 | The patched methods access these EngineCore internals:
 445 | 
 446 | - `self.scheduler` — scheduler object
 447 | - `self.scheduler.running` — set/list of running requests
 448 | - `self.scheduler.waiting` — set/list of waiting requests
 449 | - `self.scheduler.finish_requests(request_ids, RequestStatus.FINISHED_ABORTED)`
 450 | - `self.scheduler.reset_prefix_cache()` — returns bool
 451 | - `self.output_queue.put_nowait((client_index, engine_core_outputs))`
 452 | - `self.collective_rpc(method_name, args=(...))` — calls worker methods
 453 | 
 454 | Request objects in `scheduler.running` / `scheduler.waiting` have:
 455 | 
 456 | - `.request_id`
 457 | - `.client_index`
 458 | 
 459 | **Check:** Does `EngineCore` still have `scheduler`, `output_queue` attributes? Does
 460 | `scheduler` still have `running`, `waiting`, `finish_requests()`, `reset_prefix_cache()`
 461 | methods? Does `EngineCore` still have `collective_rpc()` and `call_utility_async()`? Has
 462 | the scheduler API changed (e.g., different method for aborting requests)? Is there now a
 463 | built-in `abort_all` method that replaces the monkey-patch?
 464 | 
 465 | ______________________________________________________________________
 466 | 
 467 | ### 12. `vllm.v1.engine.output_processor`
 468 | 
 469 | **Source:** `vllm-src/vllm/v1/engine/output_processor.py`
 470 | 
 471 | #### `RequestState`
 472 | 
 473 | Used via TYPE_CHECKING import in `areal_vllm_server.py:30-31`:
 474 | 
 475 | ```python
 476 | if TYPE_CHECKING:
 477 |     from vllm.v1.engine.output_processor import RequestState
 478 | ```
 479 | 
 480 | Used in the `finish_request` monkey-patch at `areal_vllm_server.py:411`:
 481 | 
 482 | ```python
 483 | def finish_request(self, req_state: "RequestState"):
 484 |     if req_state.lora_name is None:
 485 |         return
 486 |     lora_stats = self.lora_name_to_stats[req_state.lora_name]
 487 |     if req_state.request_id in lora_stats.running_requests:
 488 |         lora_stats.running_requests.remove(req_state.request_id)
 489 | ```
 490 | 
 491 | **Check:** Does `RequestState` still have `.lora_name` and `.request_id` attributes? Was
 492 | this class moved? Was it renamed?
 493 | 
 494 | ______________________________________________________________________
 495 | 
 496 | ### 13. `vllm.v1.metrics.stats`
 497 | 
 498 | **Source:** `vllm-src/vllm/v1/metrics/stats.py`
 499 | 
 500 | #### `LoRARequestStates`
 501 | 
 502 | Monkey-patched in `areal_vllm_server.py:444-448`:
 503 | 
 504 | ```python
 505 | setattr(LoRARequestStates, "finish_request", finish_request)
 506 | ```
 507 | 
 508 | This patch is guarded by a version check:
 509 | 
 510 | ```python
 511 | if not pkg_version.is_version_greater_or_equal("vllm", "0.12.0"):
 512 |     setattr(LoRARequestStates, "finish_request", finish_request)
 513 | ```
 514 | 
 515 | **Check:** Does `LoRARequestStates` still exist at this path? Does it still have a
 516 | `finish_request` method? Has the bug (that the monkey-patch fixes) been fixed upstream?
 517 | Does `LoRARequestStates` still have `.lora_name_to_stats` dict with `.running_requests`
 518 | set? If `vllm >= 0.12.0`, is the patch correctly skipped?
 519 | 
 520 | ______________________________________________________________________
 521 | 
 522 | ### 14. `vllm.v1.request`
 523 | 
 524 | **Source:** `vllm-src/vllm/v1/request.py`
 525 | 
 526 | #### `RequestStatus`
 527 | 
 528 | Used in `areal_vllm_server.py:368`:
 529 | 
 530 | ```python
 531 | scheduler.finish_requests(request_ids, RequestStatus.FINISHED_ABORTED)
 532 | ```
 533 | 
 534 | **Check:** `.FINISHED_ABORTED` enum value still exists? Was `RequestStatus` moved?
 535 | 
 536 | ______________________________________________________________________
 537 | 
 538 | ### 15. `vllm.lora.request`
 539 | 
 540 | **Source:** `vllm-src/vllm/lora/request.py`
 541 | 
 542 | #### `LoRARequest`
 543 | 
 544 | Imported in both `areal_vllm_server.py:20` and `vllm_worker_extension.py:8`.
 545 | 
 546 | Constructed in `areal_vllm_server.py:154-161` (attribute-set pattern):
 547 | 
 548 | ```python
 549 | lora_request = LoRARequest(
 550 |     lora_name=lora_name,
 551 |     lora_int_id=lora_int_id,
 552 |     lora_path=runtime_lora_path,
 553 | )
 554 | if base_model_name is not None:
 555 |     lora_request.base_model_name = base_model_name
 556 | ```
 557 | 
 558 | Constructed in `vllm_worker_extension.py:59-64` (constructor arg pattern):
 559 | 
 560 | ```python
 561 | LoRARequest(
 562 |     lora_name=lora_name,
 563 |     lora_int_id=lora_int_id,
 564 |     lora_path=lora_model_path,
 565 |     base_model_name=base_model_name,
 566 | )
 567 | ```
 568 | 
 569 | **Check:** Constructor params. Is `base_model_name` still accepted as constructor arg?
 570 | Is it still settable as an attribute? Renamed fields?
 571 | 
 572 | ______________________________________________________________________
 573 | 
 574 | ### 16. `vllm.lora.lora_model`
 575 | 
 576 | **Source:** `vllm-src/vllm/lora/lora_model.py`
 577 | 
 578 | #### `LoRAModel.from_lora_tensors(...)`
 579 | 
 580 | Called in `vllm_worker_extension.py:235`:
 581 | 
 582 | ```python
 583 | LoRAModel.from_lora_tensors(
 584 |     lora_model_id=self.areal_lora_int_id,
 585 |     tensors=normalized_weights,
 586 |     peft_helper=peft_helper,
 587 |     device=self.model_runner.device,
 588 |     dtype=self.model_runner.lora_manager.lora_config.lora_dtype,
 589 |     model_vocab_size=model_vocab_size,
 590 |     weights_mapper=getattr(self.model_runner.model, "hf_to_vllm_mapper", None),
 591 | )
 592 | ```
 593 | 
 594 | **Check:** `from_lora_tensors` class method still exists? Signature unchanged? New
 595 | required params? `weights_mapper` param still accepted?
 596 | 
 597 | ______________________________________________________________________
 598 | 
 599 | ### 17. `vllm.lora.peft_helper`
 600 | 
 601 | **Source:** `vllm-src/vllm/lora/peft_helper.py`
 602 | 
 603 | #### `PEFTHelper.from_dict(config)`
 604 | 
 605 | Called in `vllm_worker_extension.py:226`:
 606 | 
 607 | ```python
 608 | peft_config = {
 609 |     "r": self.areal_lora_rank,
 610 |     "lora_alpha": self.areal_lora_alpha,
 611 |     "target_modules": self.areal_lora_target_modules,
 612 |     "bias": self.areal_lora_bias,
 613 | }
 614 | peft_helper = PEFTHelper.from_dict(peft_config)
 615 | ```
 616 | 
 617 | **Check:** `from_dict` class method still exists? Expected dict keys unchanged?
 618 | 
 619 | ______________________________________________________________________
 620 | 
 621 | ### 18. `vllm.model_executor.model_loader`
 622 | 
 623 | **Source:** `vllm-src/vllm/model_executor/model_loader/__init__.py`
 624 | 
 625 | #### `get_model_loader(load_config)`
 626 | 
 627 | Called in `vllm_worker_extension.py:32`:
 628 | 
 629 | ```python
 630 | model_loader = get_model_loader(self.model_runner.vllm_config.load_config)
 631 | ```
 632 | 
 633 | Then used as:
 634 | 
 635 | ```python
 636 | model_loader.load_weights(
 637 |     self.model_runner.model, model_config=self.model_runner.model_config
 638 | )
 639 | ```
 640 | 
 641 | **Check:** `get_model_loader` still exists? Return type still has
 642 | `load_weights(model, model_config=...)` method? Was it moved to a different module?
 643 | 
 644 | ______________________________________________________________________
 645 | 
 646 | ### 19. `vllm.envs`
 647 | 
 648 | **Source:** `vllm-src/vllm/envs.py`
 649 | 
 650 | #### `VLLM_USE_V1` (no longer directly checked)
 651 | 
 652 | Previously checked via `if envs.VLLM_USE_V1:` in platform files. AReaL now uses a
 653 | try/except import pattern instead in `cuda.py:31-53` and `unknown.py:31-53`:
 654 | 
 655 | ```python
 656 | @classmethod
 657 | def get_vllm_worker_class(clas):
 658 |     try:
 659 |         from vllm.v1.worker.gpu_worker import Worker
 660 |         return Worker
 661 |     except ImportError:
 662 |         pass
 663 |     try:
 664 |         from vllm.worker.worker import Worker
 665 |         return Worker
 666 |     except ImportError as e:
 667 |         raise RuntimeError("vLLM is not installed or not properly configured.") from e
 668 | ```
 669 | 
 670 | **Check:** Does `vllm.v1.worker.gpu_worker.Worker` still exist? Was V0
 671 | `vllm.worker.worker.Worker` removed entirely? Are there other env vars in `vllm.envs`
 672 | that AReaL might need?
 673 | 
 674 | ______________________________________________________________________
 675 | 
 676 | ### 20. `vllm.v1.worker.gpu_worker` / `vllm.worker.worker`
 677 | 
 678 | **Source:** `vllm-src/vllm/v1/worker/gpu_worker.py` and `vllm-src/vllm/worker/worker.py`
 679 | 
 680 | #### `Worker`
 681 | 
 682 | Imported in `cuda.py` and `unknown.py` for `get_vllm_worker_class()` using try/except
 683 | (see Section 19 above).
 684 | 
 685 | **Check:** `Worker` class still exists at these paths? Was V0 `vllm.worker.worker`
 686 | removed? Was V1 worker moved?
 687 | 
 688 | ______________________________________________________________________
 689 | 
 690 | ### 21. Private/internal APIs used by AReaL
 691 | 
 692 | These are internal vLLM APIs not part of the public interface. They are most likely to
 693 | break on upgrade.
 694 | 
 695 | #### Worker extension model runner internals
 696 | 
 697 | Accessed in `vllm_worker_extension.py`:
 698 | 
 699 | - `self.model_runner.model_config.model` — writable string field (line 31)
 700 | - `self.model_runner.vllm_config.load_config` — VllmConfig load config (line 32)
 701 | - `self.model_runner.model` — the loaded model object (line 35, 144)
 702 | - `self.model_runner.model.load_weights(weights=[(name, tensor)])` — weight loading
 703 |   (line 144)
 704 | - `self.model_runner.device` — torch device (line 136, 200, 239)
 705 | - `self.model_runner.lora_manager` — LoRA manager instance (line 58, 173, 177, 214)
 706 | - `self.model_runner.lora_manager.remove_adapter(lora_int_id)` (line 58, 214)
 707 | - `self.model_runner.lora_manager.list_adapters()` (line 177)
 708 | - `self.model_runner.lora_manager.lora_config.lora_dtype` (line 240)
 709 | - `self.model_runner.lora_manager.lora_config.lora_extra_vocab_size` (line 230)
 710 | - `self.model_runner.lora_manager.vocab_size` (line 233)
 711 | - `self.model_runner.lora_manager._adapter_manager` — private adapter manager (line 185)
 712 | - `self.model_runner.lora_manager._adapter_manager._registered_adapters[id]` — private
 713 |   dict (line 185)
 714 | - `self.model_runner.lora_manager._adapter_manager._add_adapter(model)` — private method
 715 |   (line 247)
 716 | - `self.model_runner.lora_manager._adapter_manager.activate_adapter(id)` — private
 717 |   method (line 248)
 718 | - `self.model_runner.model.hf_to_vllm_mapper` — optional attribute (line 243)
 719 | - `self.model_runner.add_lora(lora_request)` — public method for disk-based LoRA loading
 720 |   (line 66)
 721 | - `self.rank` — worker rank (line 279)
 722 | 
 723 | **Check:** All `model_runner` attributes still exist? Has `lora_manager` been
 724 | restructured? Are `_adapter_manager`, `_registered_adapters`, `_add_adapter`,
 725 | `activate_adapter` still available? Has `load_weights` signature changed on the model
 726 | object? Does `add_lora` still exist on `model_runner`?
 727 | 
 728 | #### EngineCore internals (monkey-patched)
 729 | 
 730 | Accessed by injected methods in `areal_vllm_server.py`:
 731 | 
 732 | - `self.scheduler` — scheduler instance
 733 | - `self.scheduler.running` — iterable of running requests
 734 | - `self.scheduler.waiting` — iterable of waiting requests
 735 | - `self.scheduler.finish_requests(request_ids, status)` — abort method
 736 | - `self.scheduler.reset_prefix_cache()` — returns bool
 737 | - `self.output_queue` — async queue
 738 | - `self.output_queue.put_nowait((client_index, outputs))` — enqueue outputs
 739 | - `self.collective_rpc(method, args=())` — RPC to workers
 740 | - `req.request_id` — on request objects in scheduler queues
 741 | - `req.client_index` — on request objects in scheduler queues
 742 | 
 743 | **Check:** All scheduler attributes/methods still exist? Was `output_queue` renamed or
 744 | restructured? Was `collective_rpc` moved or its signature changed?
 745 | 
 746 | #### Engine client APIs (called from route handlers)
 747 | 
 748 | Accessed via `raw_request.app.state.engine_client` in `areal_vllm_server.py`:
 749 | 
 750 | - `llm.engine_core.call_utility_async(method, *args)` — calls utility method on engine
 751 |   core (lines 173, 188, 202, 214, 298)
 752 | - `llm.collective_rpc(method, args=(...))` — calls method on all workers (lines 233,
 753 |   253, 273)
 754 | 
 755 | **Check:** Does `engine_client` still expose `engine_core` with `call_utility_async()`?
 756 | Does it still expose `collective_rpc()`?
 757 | 
 758 | #### openai_serving_models internals (runtime LoRA registration)
 759 | 
 760 | Accessed in `areal_vllm_server.py:116-166`:
 761 | 
 762 | - `app.state.openai_serving_models` — serving models state object
 763 | - `serving_models.lora_requests` — dict of LoRA requests (name -> LoRARequest)
 764 | - `request.lora_path` — path attribute on LoRARequest
 765 | - `request.lora_int_id` — int id attribute on LoRARequest
 766 | 
 767 | **Check:** Does `app.state.openai_serving_models` still exist? Does it still have a
 768 | `lora_requests` dict? Are the attribute names on LoRARequest objects unchanged?
 769 | 
 770 | ______________________________________________________________________
 771 | 
 772 | ### 22. Environment variables
 773 | 
 774 | Used in `vllm_server.py` and `vllm_remote.py`:
 775 | 
 776 | - `VLLM_CACHE_ROOT` — vLLM compile cache directory
 777 | - `VLLM_ALLOW_RUNTIME_LORA_UPDATING` — set to `"True"` to enable runtime LoRA updates
 778 | 
 779 | **Check:** These env vars still recognized by vLLM? Any renamed? Any new required env
 780 | vars?
 781 | 
 782 | ______________________________________________________________________
 783 | 
 784 | ### 23. vLLM server CLI interface
 785 | 
 786 | AReaL builds vLLM CLI commands in `areal/api/cli_args.py` (`vLLMConfig` dataclass). The
 787 | CLI flags are converted to command-line arguments via `get_py_cmd()`:
 788 | 
 789 | ```python
 790 | vLLMConfig.build_cmd_from_args(args)
 791 | # → python3 -m areal.engine.vllm_ext.areal_vllm_server --model ... --seed ...
 792 | ```
 793 | 
 794 | Fields in `vLLMConfig` that map to vLLM CLI flags:
 795 | 
 796 | - `--model`, `--tokenizer`, `--seed`
 797 | - `--skip-tokenizer-init`, `--enforce-eager`
 798 | - `--dtype`, `--distributed-executor-backend`
 799 | - `--max-num-seqs`, `--block-size`, `--swap-space`
 800 | - `--cpu-offload-gb`, `--disable-sliding-window`
 801 | - `--max-model-len`
 802 | - `--no-enable-chunked-prefill`, `--no-enable-prefix-caching`
 803 | - `--gpu-memory-utilization`
 804 | - `--worker-extension-cls`
 805 | - `--enable-sleep-mode`, `--uvicorn-log-level`
 806 | - `--enable-lora`, `--max-lora-rank`, `--max-loras`, `--lora-modules`
 807 | - `--load-format`, `--trust-remote-code`
 808 | - `--tensor-parallel-size`, `--pipeline-parallel-size`
 809 | - `--host`, `--port`
 810 | 
 811 | **Check:** All CLI flags still accepted? Any renamed (e.g.,
 812 | `--distributed-executor-backend`)? Any removed? New required flags? Has
 813 | `--worker-extension-cls` been renamed or removed? Has `--no-enable-chunked-prefill`
 814 | behavior changed? Does `--enable-sleep-mode` still exist (enables `/sleep` and
 815 | `/wake_up` endpoints)?
 816 | 
 817 | ______________________________________________________________________
 818 | 
 819 | ### 24. vLLM HTTP endpoints
 820 | 
 821 | AReaL interacts with vLLM via HTTP. The following endpoints are used:
 822 | 
 823 | **Standard vLLM endpoints:**
 824 | 
 825 | - `GET /health` — health check (`vllm_remote.py:221`)
 826 | - `GET /v1/models` — server readiness check (`vllm_server.py:72`)
 827 | - `POST /v1/completions` — text generation (`vllm_remote.py:90`,
 828 |   `areal_vllm_server.py:316`)
 829 | - `POST /v1/chat/completions` — VLM chat generation (`vllm_remote.py:87`)
 830 | - `POST /v1/load_lora_adapter` — load LoRA adapter from disk (`vllm_remote.py:131`)
 831 | - `POST /sleep` — offload model to CPU (`vllm_remote.py:229`)
 832 | - `POST /wake_up` — reload model from CPU, with optional `?tags=` query
 833 |   (`vllm_remote.py:248`)
 834 | 
 835 | **Custom AReaL endpoints** (registered via `@router.post` in `areal_vllm_server.py`):
 836 | 
 837 | - `POST /areal_update_weights` — update full model weights from disk
 838 | - `POST /areal_update_weights_lora` — update LoRA weights from disk
 839 | - `POST /areal_update_weights_xccl` — update full model weights via NCCL/HCCL
 840 | - `POST /areal_update_weights_lora_xccl` — update LoRA weights via NCCL/HCCL
 841 | - `POST /areal_init_weights_update_group` — initialize distributed weight update group
 842 | - `POST /areal_set_update_weight_meta` — set weight metadata for XCCL update
 843 | - `POST /areal_set_update_weight_meta_lora` — set LoRA weight metadata for XCCL update
 844 | - `POST /areal_pause_generation` — pause generation and abort all requests
 845 | - `POST /areal_continue_generation` — resume generation
 846 | 
 847 | **Check:** Standard endpoints still at same paths? Response format unchanged? `/sleep`
 848 | and `/wake_up` still exist? `/v1/completions` response still has
 849 | `choices[0].logprobs.tokens` or `choices[0].logprobs.content` format? Has
 850 | `return_tokens_as_token_ids` param changed behavior (token format `"token:123"`)?
 851 | 
 852 | ______________________________________________________________________
 853 | 
 854 | ## Version-Guarded Code
 855 | 
 856 | AReaL has version-specific code paths:
 857 | 
 858 | ```python
 859 | # areal_vllm_server.py:439-448
 860 | # Patch for LoRARequestStates management in vllm < v0.11.0
 861 | # This may be removed with vllm >= 0.12.x
 862 | from areal.utils import pkg_version
 863 | 
 864 | if not pkg_version.is_version_greater_or_equal("vllm", "0.12.0"):
 865 |     setattr(LoRARequestStates, "finish_request", finish_request)
 866 | ```
 867 | 
 868 | **Check:** If upgrading to >= 0.12.0, verify the upstream
 869 | `LoRARequestStates.finish_request` fix is present. If upgrading past the fix version,
 870 | the guarded code becomes dead code — note for cleanup.
 871 | 
 872 | Also in `areal/api/cli_args.py` (comments):
 873 | 
 874 | ```python
 875 | # IMPORTANT: vLLM V1 engine forces enable_chunked_prefill=True by default
 876 | # TODO(vllm-v0.11.0): vLLM v0.11.0 has inference quality issues when
 877 | # temperature=1.0
 878 | ```
 879 | 
 880 | **Check:** Have these known issues been fixed in the target version?
 881 | 
 882 | ______________________________________________________________________
 883 | 
 884 | ## Upgrade Workflow
 885 | 
 886 | ### Step 0: Prepare vLLM source
 887 | 
 888 | Clone or checkout the target version as described in Prerequisites above.
 889 | 
 890 | ### Step 1: Audit `vllm` API signatures
 891 | 
 892 | For EACH entry in the API Usage Catalog above:
 893 | 
 894 | 1. Open the upstream source file at the target version.
 895 | 1. Compare the function/class signature against the current AReaL invocation.
 896 | 1. Flag any of:
 897 |    - **Removed parameters** still passed by AReaL → must remove from call site
 898 |    - **Renamed parameters** → must rename in call site
 899 |    - **New required parameters** (no default) → must add to call site
 900 |    - **New optional parameters** with useful defaults → document but skip
 901 |    - **Changed return types** → must update consumers
 902 |    - **Removed functions/classes** → must find replacement
 903 |    - **Moved modules** → must update import paths
 904 |    - **Changed method signatures** on returned/internal objects → must update call sites
 905 | 1. Record findings per-file.
 906 | 
 907 | ### Step 2: Audit private/internal API compatibility
 908 | 
 909 | vLLM's internal APIs (Section 21) are the most fragile. For each:
 910 | 
 911 | 1. Search the upstream source for the accessed attribute/method.
 912 | 1. Verify it still exists at the expected path.
 913 | 1. Check if vLLM has added official APIs that replace the private access patterns.
 914 | 1. If an official API exists, prefer migrating to it over maintaining private API
 915 |    access.
 916 | 
 917 | ### Step 3: Audit vLLM CLI flag compatibility
 918 | 
 919 | Compare `vLLMConfig` fields in `areal/api/cli_args.py` against the vLLM CLI:
 920 | 
 921 | ```bash
 922 | cd vllm-src && python -m vllm.entrypoints.openai.api_server --help
 923 | ```
 924 | 
 925 | Flag any removed/renamed CLI arguments.
 926 | 
 927 | ### Step 4: Update `pyproject.toml`
 928 | 
 929 | Update the `vllm` version pin in `pyproject.toml`:
 930 | 
 931 | ```toml
 932 | vllm = [
 933 | "vllm==X.Y.Z; sys_platform == 'linux' and platform_machine == 'x86_64'",
 934 | ]
 935 | ```
 936 | 
 937 | Run `uv lock` to verify dependency resolution.
 938 | 
 939 | ### Step 5: Apply code changes
 940 | 
 941 | For each flagged incompatibility from Steps 1-3:
 942 | 
 943 | 1. Update the call site in the affected file.
 944 | 1. Preserve existing behavior — do NOT refactor beyond what's required.
 945 | 1. If a function was removed, check the upstream migration guide or changelog.
 946 | 1. If a module was moved, update the import path.
 947 | 
 948 | Priority order for applying changes:
 949 | 
 950 | 1. `areal/engine/vllm_ext/areal_vllm_server.py` (highest risk — monkey-patches, V1
 951 |    engine internals, many imports)
 952 | 1. `areal/engine/vllm_ext/vllm_worker_extension.py` (private API consumer — model
 953 |    runner, LoRA manager)
 954 | 1. `areal/engine/vllm_remote.py` (HTTP interface — response parsing, endpoint paths)
 955 | 1. `areal/infra/platforms/cuda.py` (V0/V1 worker import)
 956 | 1. `areal/infra/platforms/unknown.py` (same as cuda.py)
 957 | 1. `areal/infra/launcher/vllm_server.py` (env vars, server lifecycle)
 958 | 1. `areal/api/cli_args.py` (`vLLMConfig` — CLI flag mapping)
 959 | 1. `areal/infra/launcher/ray.py`
 960 | 1. `areal/infra/launcher/local.py`
 961 | 1. `areal/infra/launcher/slurm.py`
 962 | 1. `areal/trainer/rl_trainer.py`
 963 | 1. Test files
 964 | 
 965 | ### Step 6: Update version-guarded code
 966 | 
 967 | 1. Review the `pkg_version.is_version_greater_or_equal("vllm", "0.12.0")` guard in
 968 |    `areal_vllm_server.py`. If upgrading to >= 0.12.0, verify the upstream fix and
 969 |    potentially remove the dead code path.
 970 | 1. Review TODO comments referencing specific vLLM versions.
 971 | 
 972 | ### Step 7: Run pre-commit and tests
 973 | 
 974 | ```bash
 975 | pre-commit run --all-files
 976 | uv run pytest tests/test_inference_engines.py -v
 977 | uv run pytest tests/test_model_utils.py -v
 978 | uv run pytest tests/test_allocation_mode.py -v
 979 | ```
 980 | 
 981 | If a GPU with vLLM installed is available:
 982 | 
 983 | ```bash
 984 | uv run pytest tests/test_examples.py -v -k vllm
 985 | ```
 986 | 
 987 | ### Step 8: Report changes
 988 | 
 989 | Output a summary in this format:
 990 | 
 991 | ```
 992 | ## Upgrade Summary: vLLM ${OLD_VERSION} → ${NEW_VERSION}
 993 | 
 994 | ### Breaking Changes Found
 995 | - [file:line] description of change needed
 996 | 
 997 | ### Module Moves / Renames
 998 | - [old_path] → [new_path] (affects: list of AReaL files)
 999 | 
1000 | ### Private API Changes
1001 | - [internal_api] description of change (affects: list of AReaL files)
1002 | 
1003 | ### CLI Flag Changes
1004 | - [flag] description (affects: vLLMConfig in cli_args.py)
1005 | 
1006 | ### API Additions (new optional params, informational)
1007 | - [upstream_file] description
1008 | 
1009 | ### Files Modified
1010 | - path/to/file.py: description of change
1011 | 
1012 | ### Version-Guarded Code
1013 | - [file:line] status of version guard (still needed / can be removed)
1014 | 
1015 | ### Tests
1016 | - ✅ pre-commit passed
1017 | - ✅ test_inference_engines passed
1018 | - ✅ test_model_utils passed
1019 | - ✅ test_allocation_mode passed
1020 | - ⬚ integration tests (requires GPU with vLLM installed)
1021 | ```
1022 | 
1023 | If there are unresolvable breaking changes, STOP and ask the user before proceeding.
```


---
## .claude/skills/add-archon-model/SKILL.md

```
   1 | ---
   2 | name: add-archon-model
   3 | description: Guide for adding a new model to the Archon engine. Use when user wants to add support for a new HuggingFace model architecture in ArchonEngine.
   4 | ---
   5 | 
   6 | # Add Archon Model
   7 | 
   8 | Add support for a new HuggingFace model architecture in the Archon training engine.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a model to Archon?"
  15 | - User wants to support a new model family (e.g., Llama, Mistral, DeepSeek) in
  16 |   ArchonEngine
  17 | - User mentions adding a new `ModelSpec` or model type for Archon
  18 | 
  19 | ## Prerequisites
  20 | 
  21 | Before starting, ensure:
  22 | 
  23 | - The target model is available on HuggingFace (has `config.json` with `model_type`)
  24 | - You know the HuggingFace model ID (e.g., `meta-llama/Llama-3-8B`)
  25 | - The model uses a standard transformer architecture (decoder-only)
  26 | 
  27 | ## Step-by-Step Guide
  28 | 
  29 | ### Step 1: Analyze the Target Model Architecture
  30 | 
  31 | Read the HuggingFace model's source code to extract key architecture information.
  32 | 
  33 | **Action**: Fetch and analyze the model's HuggingFace configuration and modeling files.
  34 | 
  35 | 1. Read the model's `config.json` (via `AutoConfig.from_pretrained`) to identify:
  36 | 
  37 |    - `model_type` string (this is the key used for registry lookup)
  38 |    - All architecture hyperparameters (hidden_size, num_layers, etc.)
  39 |    - Any model-specific fields (e.g., `qk_norm`, `attention_bias`, MoE fields)
  40 | 
  41 | 1. Read the HuggingFace `modeling_*.py` source to identify:
  42 | 
  43 |    - **Attention variant**: Does it have Q/K norm? Attention bias? Sliding window?
  44 |      Multi-latent attention?
  45 |    - **FFN variant**: SwiGLU (gate_proj + up_proj + down_proj)? GeGLU? Standard MLP?
  46 |    - **MoE support**: Does it have MoE layers? What router type? Shared experts?
  47 |    - **RoPE variant**: Standard RoPE? YaRN? NTK-aware scaling? What is the inv_freq
  48 |      formula?
  49 |    - **Normalization**: RMSNorm or LayerNorm? Pre-norm or post-norm? Elementwise affine?
  50 |    - **Weight tying**: Does `tie_word_embeddings` appear in config?
  51 |    - **State dict key names**: What are the HF weight key naming conventions?
  52 | 
  53 | 1. Summarize findings in a checklist like:
  54 | 
  55 | ```
  56 | Target model: <name>
  57 | HF model_type: "<model_type>" (and variants like "<model_type>_moe" if applicable)
  58 | Attention: [standard GQA / with QK norm / with bias / sliding window / ...]
  59 | FFN: [SwiGLU / GeGLU / standard MLP / ...]
  60 | MoE: [no / yes - num_experts, top_k, shared_experts]
  61 | RoPE: [standard / YaRN / NTK-aware / ...]
  62 | Norm: [RMSNorm / LayerNorm] with [pre-norm / post-norm]
  63 | Weight tying: [yes / no]
  64 | ```
  65 | 
  66 | ### Step 2: Select the Reference Model
  67 | 
  68 | Choose the closest existing implementation as a starting point:
  69 | 
  70 | | Target characteristics               | Reference | Why                                     |
  71 | | ------------------------------------ | --------- | --------------------------------------- |
  72 | | Dense-only, standard GQA, no QK norm | `qwen2`   | Simplest baseline, pure dense           |
  73 | | Has QK norm, or has MoE support      | `qwen3`   | Supports QK norm + MoE + shared experts |
  74 | 
  75 | **Action**: Copy the reference model directory as the starting point:
  76 | 
  77 | ```
  78 | areal/experimental/models/archon/<model>/
  79 |   __init__.py
  80 |   spec.py
  81 |   model/
  82 |     args.py
  83 |     model.py
  84 |     rope.py
  85 |     state_dict_adapter.py
  86 |   infra/
  87 |     parallelize.py
  88 | ```
  89 | 
  90 | ### Step 3: Implement `args.py`
  91 | 
  92 | Adapt `<Model>ModelArgs` to match the target model's HuggingFace config fields.
  93 | 
  94 | **Key changes from reference**:
  95 | 
  96 | 1. Update the `@dataclass` fields to match the target model's hyperparameters:
  97 | 
  98 |    - Field names should use Archon conventions (`dim`, `n_layers`, `n_heads`,
  99 |      `n_kv_heads`, `vocab_size`, `head_dim`, `hidden_dim`, `norm_eps`, `rope_theta`,
 100 |      etc.)
 101 |    - Default values should match the smallest variant of the target model
 102 |    - Add model-specific fields (e.g., `attention_bias`, `qk_norm`, `sliding_window`)
 103 | 
 104 | 1. Update `from_hf_config()` to correctly map HuggingFace config attributes:
 105 | 
 106 |    - Use `getattr(hf_config, "field_name", default)` for optional fields
 107 |    - Handle variant-specific fields (e.g., MoE fields only present in MoE variants)
 108 |    - The method must return an instance of the model args class
 109 | 
 110 | **Critical**: Verify every field mapping against the HF model's `config.json`. Incorrect
 111 | mappings here cause silent errors downstream.
 112 | 
 113 | **Base class contract** (`BaseModelArgs`):
 114 | 
 115 | ```python
 116 | @dataclass
 117 | class <Model>ModelArgs(BaseModelArgs):
 118 |     # ... model-specific fields ...
 119 | 
 120 |     @classmethod
 121 |     def from_hf_config(
 122 |         cls,
 123 |         hf_config: PretrainedConfig,
 124 |         is_critic: bool = False,
 125 |         **kwargs,
 126 |     ) -> <Model>ModelArgs:
 127 |         # Map HF config fields to Archon model args
 128 |         ...
 129 | ```
 130 | 
 131 | ### Step 4: Implement `model.py`
 132 | 
 133 | Adapt the model architecture to match the target model.
 134 | 
 135 | **Key components to adapt**:
 136 | 
 137 | 1. **Normalization** (`RMSNorm` or similar):
 138 | 
 139 |    - Check if `elementwise_affine` is configurable
 140 |    - Check the epsilon default value
 141 |    - If the model uses `LayerNorm`, implement accordingly
 142 | 
 143 | 1. **Attention** module:
 144 | 
 145 |    - Q/K/V projection: Check bias presence (`nn.Linear(..., bias=True/False)`)
 146 |    - QK norm: Add `q_norm`/`k_norm` if the model has them, remove if it doesn't
 147 |    - GQA: `n_kv_heads` \< `n_heads` for grouped-query attention
 148 |    - Ulysses SP: Keep the `set_cp_group` / `_sp_enabled` pattern from the reference
 149 |    - Output projection: Check bias presence
 150 | 
 151 | 1. **FeedForward** module:
 152 | 
 153 |    - SwiGLU: `w2(silu(w1(x)) * w3(x))` -- most common for modern LLMs
 154 |    - Check bias in linear layers
 155 |    - For MoE models: `MoE` module replaces `FeedForward` on designated layers
 156 | 
 157 | 1. **TransformerBlock**: Pre-norm (most modern LLMs) vs post-norm
 158 | 
 159 |    - MoE layer detection via `_is_moe_layer()` if applicable
 160 | 
 161 | 1. **Top-level Model** (`<Model>Model(BaseArchonModel)`):
 162 | 
 163 |    - `tok_embeddings`, `layers` (as `ModuleDict`), `norm`, `output`/`score`
 164 |    - `init_weights()`: Match initialization scheme from HF
 165 |    - `init_buffers()`: RoPE cache + MoE buffers
 166 |    - `forward()`: Must follow `BaseArchonModel` signature:
 167 |      `(tokens, positions, cu_seqlens, max_seqlen, tree_attn_meta=None) -> Tensor`
 168 | 
 169 | **Base class contract** (`BaseArchonModel`):
 170 | 
 171 | ```python
 172 | class <Model>Model(BaseArchonModel):
 173 |     def forward(self, tokens, positions, cu_seqlens, max_seqlen, tree_attn_meta=None) -> torch.Tensor: ...
 174 |     def init_weights(self) -> None: ...
 175 |     def init_buffers(self, buffer_device) -> None: ...
 176 | ```
 177 | 
 178 | ### Step 5: Implement `rope.py`
 179 | 
 180 | Handle the rotary position embedding variant.
 181 | 
 182 | **Options**:
 183 | 
 184 | 1. **Standard RoPE** (same as qwen2/qwen3): Re-export from qwen2:
 185 | 
 186 |    ```python
 187 |    from areal.experimental.models.archon.qwen2.model.rope import (
 188 |        apply_rotary_emb,
 189 |        precompute_rope_cache,
 190 |        repeat_kv,
 191 |        reshape_for_broadcast,
 192 |        rotate_half,
 193 |    )
 194 |    ```
 195 | 
 196 | 1. **Custom RoPE** (YaRN, NTK-aware, etc.): Implement custom `precompute_rope_cache()`
 197 |    and `apply_rotary_emb()` functions. The key difference is usually in how `inv_freq`
 198 |    is computed (scaling factors, interpolation, etc.).
 199 | 
 200 | ### Step 6: Implement `state_dict_adapter.py`
 201 | 
 202 | Map between HuggingFace and Archon weight key names.
 203 | 
 204 | **This is the most error-prone step.** The adapter must correctly handle:
 205 | 
 206 | 1. **Key name mapping** (`from_hf_map` dict):
 207 | 
 208 |    - Embedding: `model.embed_tokens.weight` -> `tok_embeddings.weight`
 209 |    - Attention: `model.layers.{}.self_attn.q_proj.weight` ->
 210 |      `layers.{}.attention.wq.weight`
 211 |    - FFN: `model.layers.{}.mlp.gate_proj.weight` -> `layers.{}.feed_forward.w1.weight`
 212 |    - Norms: `model.layers.{}.input_layernorm.weight` ->
 213 |      `layers.{}.attention_norm.weight`
 214 |    - Output: `lm_head.weight` -> `output.weight`
 215 |    - Skip keys (set to `None`): `rotary_emb.inv_freq` (computed at runtime)
 216 |    - Model-specific keys: bias terms, QK norm weights, etc.
 217 | 
 218 | 1. **Reverse mapping** (`to_hf_map`): Auto-generated from `from_hf_map`
 219 | 
 220 | 1. **MoE expert weights** (if applicable): 3D\<->2D conversion for expert weights. Copy
 221 |    the MoE handling from qwen3 if the model has MoE.
 222 | 
 223 | 1. **Weight tying**: Skip `output.weight` during `to_hf()` if `tie_word_embeddings=True`
 224 | 
 225 | **Verification approach**: After implementation, the adapter should satisfy:
 226 | 
 227 | ```python
 228 | # Roundtrip: archon -> hf -> archon preserves all keys
 229 | hf_sd = adapter.to_hf(archon_sd)
 230 | roundtrip_sd = adapter.from_hf(hf_sd)
 231 | assert set(roundtrip_sd.keys()) == set(archon_sd.keys())
 232 | ```
 233 | 
 234 | **Base class contract** (`BaseStateDictAdapter`):
 235 | 
 236 | ```python
 237 | class <Model>StateDictAdapter(BaseStateDictAdapter):
 238 |     def from_hf(self, hf_state_dict) -> dict[str, Any]: ...
 239 |     def to_hf(self, archon_state_dict) -> dict[str, Any]: ...
 240 |     def convert_single_to_hf(self, name, tensor) -> list[tuple[str, torch.Tensor]]: ...
 241 | ```
 242 | 
 243 | ### Step 7: Implement `parallelize.py`
 244 | 
 245 | Define the parallelization strategy for the model.
 246 | 
 247 | **The parallelize function** applies parallelism in this order:
 248 | 
 249 | 1. TP (Tensor Parallelism) -- shard attention/FFN across devices
 250 | 1. EP (Expert Parallelism) -- for MoE models only
 251 | 1. CP (Context Parallelism / Ulysses SP) -- sequence parallelism
 252 | 1. AC (Activation Checkpointing) -- memory optimization
 253 | 1. torch.compile -- compilation optimization
 254 | 1. FSDP (Fully Sharded Data Parallelism) -- data parallelism
 255 | 
 256 | **Key adaptations by model architecture**:
 257 | 
 258 | - **Attention with QK norm**: wq/wk use `use_local_output=False` (DTensor output for
 259 |   norm), add `SequenceParallel(sequence_dim=2)` for q_norm/k_norm
 260 | - **Attention without QK norm**: wq/wk/wv all use `use_local_output=True`
 261 | - **Attention with bias**: Bias terms follow the same parallel plan as their weights
 262 | - **MoE layers**: Separate TP plan for MoE input/output, router gate, and expert
 263 |   weights. Copy from qwen3's `apply_moe_ep_tp()` and `apply_non_moe_tp()`
 264 | - **Dense-only models**: Simpler plan without MoE handling. Copy from qwen2
 265 | 
 266 | **Function signature** (must match `ParallelizeFn` protocol):
 267 | 
 268 | ```python
 269 | def parallelize_<model>(
 270 |     model: nn.Module,
 271 |     parallel_dims: ArchonParallelDims,
 272 |     param_dtype: torch.dtype = torch.bfloat16,
 273 |     reduce_dtype: torch.dtype = torch.float32,
 274 |     loss_parallel: bool = True,
 275 |     cpu_offload: bool = False,
 276 |     reshard_after_forward_policy: str = "default",
 277 |     ac_config: ActivationCheckpointConfig | None = None,
 278 |     enable_compile: bool = True,
 279 | ) -> nn.Module:
 280 | ```
 281 | 
 282 | ### Step 8: Create `spec.py` and Register
 283 | 
 284 | Assemble the `ModelSpec` and register it.
 285 | 
 286 | ```python
 287 | from areal.experimental.models.archon.model_spec import ModelSpec, register_model_spec
 288 | from areal.experimental.models.archon.pipeline_parallel import pipeline_llm
 289 | from areal.experimental.models.archon.<model>.infra.parallelize import parallelize_<model>
 290 | from areal.experimental.models.archon.<model>.model.args import <Model>ModelArgs
 291 | from areal.experimental.models.archon.<model>.model.model import <Model>Model
 292 | from areal.experimental.models.archon.<model>.model.state_dict_adapter import (
 293 |     <Model>StateDictAdapter,
 294 | )
 295 | 
 296 | <MODEL>_SPEC = ModelSpec(
 297 |     name="<Model>",
 298 |     model_class=<Model>Model,
 299 |     model_args_class=<Model>ModelArgs,
 300 |     state_dict_adapter_class=<Model>StateDictAdapter,
 301 |     parallelize_fn=parallelize_<model>,
 302 |     supported_model_types=frozenset({"<model_type>"}),  # From HF config.json
 303 |     pipelining_fn=pipeline_llm,
 304 | )
 305 | 
 306 | # Auto-register when module is imported
 307 | register_model_spec(<MODEL>_SPEC)
 308 | 
 309 | __all__ = ["<MODEL>_SPEC"]
 310 | ```
 311 | 
 312 | **Note**: `supported_model_types` should include all HF `model_type` strings that this
 313 | implementation handles (e.g., `{"qwen3", "qwen3_moe"}` for Qwen3).
 314 | 
 315 | ### Step 9: Register in `__init__.py`
 316 | 
 317 | Add the import to `areal/experimental/models/archon/__init__.py`:
 318 | 
 319 | ```python
 320 | from areal.experimental.models.archon.<model> import spec as <model>_spec  # noqa: F401
 321 | ```
 322 | 
 323 | This triggers auto-registration when the module is imported.
 324 | 
 325 | ### Step 10: Verify and Test
 326 | 
 327 | Verification should be done in stages, adapting based on available hardware and the test
 328 | patterns in `tests/experimental/archon/`.
 329 | 
 330 | **Before writing tests**, examine the existing test files to understand current
 331 | patterns:
 332 | 
 333 | ```
 334 | tests/experimental/archon/
 335 |   conftest.py             -- Pytest configuration (version checks)
 336 |   utils.py                -- Shared utilities (model loading, comparison)
 337 |   test_qwen3_args.py      -- Args unit tests (CPU-only)
 338 |   test_state_dict_adapter.py  -- State dict roundtrip tests
 339 |   test_weight_sync.py     -- Weight completeness tests (meta device)
 340 |   test_forward.py         -- Forward precision comparison (single GPU)
 341 |   ...
 342 | ```
 343 | 
 344 | **Test stages** (write tests appropriate for the model's complexity):
 345 | 
 346 | #### Stage 1: Args Tests (CPU-only, always write these)
 347 | 
 348 | Test `from_hf_config()` with mock HuggingFace configs:
 349 | 
 350 | ```python
 351 | # Pattern: Create mock PretrainedConfig, verify args mapping
 352 | from unittest.mock import MagicMock
 353 | 
 354 | def test_args_from_hf_config():
 355 |     hf_config = MagicMock()
 356 |     hf_config.hidden_size = 4096
 357 |     hf_config.num_hidden_layers = 32
 358 |     # ... set all required fields
 359 |     args = <Model>ModelArgs.from_hf_config(hf_config)
 360 |     assert args.dim == 4096
 361 |     assert args.n_layers == 32
 362 | ```
 363 | 
 364 | #### Stage 2: State Dict Adapter Tests (CPU-only)
 365 | 
 366 | Test key mapping roundtrip:
 367 | 
 368 | ```python
 369 | def test_state_dict_roundtrip():
 370 |     # Create adapter with mock config
 371 |     adapter = <Model>StateDictAdapter(mock_config)
 372 |     # Create fake archon state dict with expected keys
 373 |     archon_sd = {"tok_embeddings.weight": torch.randn(vocab, dim), ...}
 374 |     # Roundtrip
 375 |     hf_sd = adapter.to_hf(archon_sd)
 376 |     roundtrip = adapter.from_hf(hf_sd)
 377 |     assert set(roundtrip.keys()) == set(archon_sd.keys())
 378 | ```
 379 | 
 380 | #### Stage 3: Weight Completeness (meta device, CPU-only)
 381 | 
 382 | Verify all model parameters have HF mappings:
 383 | 
 384 | ```python
 385 | def test_weight_completeness():
 386 |     # Create model on meta device
 387 |     with torch.device("meta"):
 388 |         model = <Model>Model(args)
 389 |     adapter = <Model>StateDictAdapter(hf_config)
 390 |     # Check every archon param has a HF mapping
 391 |     for name, _ in model.named_parameters():
 392 |         hf_pairs = adapter.convert_single_to_hf(name, torch.empty(0))
 393 |         assert len(hf_pairs) > 0, f"No HF mapping for {name}"
 394 | ```
 395 | 
 396 | #### Stage 4: Forward Precision (single GPU, if available)
 397 | 
 398 | Compare Archon model output against HuggingFace reference:
 399 | 
 400 | ```python
 401 | @pytest.mark.skipif(not torch.cuda.is_available(), reason="Requires CUDA")
 402 | def test_forward_matches_hf():
 403 |     # Load both HF and Archon models
 404 |     # Run forward on same input
 405 |     # Compare logits within tolerance
 406 | ```
 407 | 
 408 | **Important**: Do NOT hardcode the test categories. Inspect the existing test files in
 409 | `tests/experimental/archon/` and follow the same patterns, fixtures, and markers. Adapt
 410 | test scope to the model's specific features (e.g., add MoE-specific tests only if the
 411 | model has MoE).
 412 | 
 413 | ## Reference Implementations
 414 | 
 415 | | Model | Directory                                 | Features                                                |
 416 | | ----- | ----------------------------------------- | ------------------------------------------------------- |
 417 | | Qwen2 | `areal/experimental/models/archon/qwen2/` | Dense, attention bias, no QK norm                       |
 418 | | Qwen3 | `areal/experimental/models/archon/qwen3/` | Dense + MoE, QK norm, no attention bias, shared experts |
 419 | 
 420 | ## Architecture Decision Map
 421 | 
 422 | | Feature             | qwen2    | qwen3                      | What to check in target model                            |
 423 | | ------------------- | -------- | -------------------------- | -------------------------------------------------------- |
 424 | | Attention bias      | Yes      | No                         | `attention_bias` in HF config                            |
 425 | | QK norm             | No       | Yes                        | `qk_norm` in HF config or QKNorm module in modeling file |
 426 | | MoE                 | No       | Yes                        | `num_experts`/`num_local_experts` in HF config           |
 427 | | Shared experts      | No       | Yes                        | `num_shared_experts` in HF config                        |
 428 | | Decoder sparse step | No       | Yes                        | `decoder_sparse_step` in HF config                       |
 429 | | Weight tying        | Both     | Both                       | `tie_word_embeddings` in HF config                       |
 430 | | RoPE                | Standard | Standard (re-export qwen2) | Check inv_freq formula in HF modeling code               |
 431 | 
 432 | ## Common Mistakes
 433 | 
 434 | - Not mapping all HF keys in `state_dict_adapter.py` (causes silent weight drops)
 435 | - Wrong `from_hf_config()` field mapping (uses wrong HF config attribute name)
 436 | - Forgetting to handle `None` keys in `from_hf_map` (keys to skip like
 437 |   `rotary_emb.inv_freq`)
 438 | - Missing MoE expert weight 3D\<->2D conversion when model has MoE
 439 | - Wrong TP plan for attention with/without QK norm (`use_local_output` must match)
 440 | - Forgetting to add import line in `areal/experimental/models/archon/__init__.py`
 441 | - Not including all `model_type` variants in `supported_model_types` frozenset
 442 | - Using `print` instead of `areal.utils.logging.getLogger()`
 443 | 
 444 | ## File Checklist
 445 | 
 446 | After completion, verify all files exist and are consistent:
 447 | 
 448 | - [ ] `areal/experimental/models/archon/<model>/__init__.py`
 449 | - [ ] `areal/experimental/models/archon/<model>/spec.py` -- ModelSpec + register
 450 | - [ ] `areal/experimental/models/archon/<model>/model/args.py` -- ModelArgs +
 451 |   from_hf_config
 452 | - [ ] `areal/experimental/models/archon/<model>/model/model.py` -- Model + Attention +
 453 |   FFN
 454 | - [ ] `areal/experimental/models/archon/<model>/model/rope.py` -- RoPE (or re-export)
 455 | - [ ] `areal/experimental/models/archon/<model>/model/state_dict_adapter.py` -- Key
 456 |   mapping
 457 | - [ ] `areal/experimental/models/archon/<model>/infra/parallelize.py` -- Parallel
 458 |   strategy
 459 | - [ ] `areal/experimental/models/archon/__init__.py` -- Import line added
 460 | - [ ] `tests/experimental/archon/test_<model>_*.py` -- Tests
 461 | 
 462 | ______________________________________________________________________
 463 | 
 464 | <!--
 465 | ================================================================================
 466 |                             MAINTAINER GUIDE
 467 | ================================================================================
 468 | 
 469 | Location: .claude/skills/add-archon-model/SKILL.md
 470 | Invocation: /add-archon-model <model_name>
 471 | 
 472 | ## Purpose
 473 | 
 474 | Semi-automated guide for adding new model architectures to the Archon training engine.
 475 | Unlike simpler skills (add-reward, add-dataset), this skill actively guides Claude to:
 476 | 1. Analyze HuggingFace source code to extract architecture details
 477 | 2. Select the closest reference implementation (qwen2 or qwen3)
 478 | 3. Generate code skeletons adapted to the target architecture
 479 | 4. Create appropriate tests based on existing test patterns
 480 | 
 481 | ## How to Update
 482 | 
 483 | ### When New Reference Models Are Added
 484 | 1. Add to "Reference Implementations" table
 485 | 2. Update "Architecture Decision Map" with new feature columns
 486 | 3. Update Step 2 (reference selection) with new options
 487 | 
 488 | ### When Base Classes Change
 489 | 1. Update contract signatures in Steps 3, 4, 6, 7
 490 | 2. Update file checklist if new files are required
 491 | 
 492 | ### When ModelSpec Changes
 493 | 1. Update Step 8 with new ModelSpec fields
 494 | 2. Update spec.py template
 495 | 
 496 | ### When Test Patterns Change
 497 | 1. Update Step 10 with new test patterns
 498 | 2. Do NOT hardcode test categories -- keep it flexible
 499 | 
 500 | ### Important Design Decisions
 501 | - This skill is SEMI-AUTOMATED: Claude should read HF source and generate code,
 502 |   not just provide templates for the user to fill in manually
 503 | - The skill references existing test files rather than hardcoding test categories,
 504 |   ensuring it stays current as the test suite evolves
 505 | - Reference model selection (qwen2 vs qwen3) is based on MoE and QK norm presence
 506 | 
 507 | ================================================================================
 508 | -->
```


---
## .claude/skills/add-dataset/SKILL.md

```
   1 | ---
   2 | name: add-dataset
   3 | description: Guide for adding a new dataset loader to AReaL. Use when user wants to add a new dataset.
   4 | ---
   5 | 
   6 | # Add Dataset
   7 | 
   8 | Add a new dataset loader to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a dataset?"
  15 | - User wants to integrate a new dataset
  16 | - User mentions creating a dataset loader
  17 | 
  18 | ## Step-by-Step Guide
  19 | 
  20 | ### Step 1: Create Dataset File
  21 | 
  22 | Create `areal/dataset/<name>.py`:
  23 | 
  24 | ```python
  25 | from datasets import Dataset, load_dataset
  26 | 
  27 | 
  28 | def get_<name>_sft_dataset(
  29 |     path: str,
  30 |     split: str,
  31 |     tokenizer,
  32 |     max_length: int | None = None,
  33 | ) -> Dataset:
  34 |     """Load dataset for SFT training.
  35 | 
  36 |     Args:
  37 |         path: Path to dataset (HuggingFace hub or local path)
  38 |         split: Dataset split (train/validation/test)
  39 |         tokenizer: Tokenizer for processing
  40 |         max_length: Maximum sequence length (optional)
  41 | 
  42 |     Returns:
  43 |         HuggingFace Dataset with processed samples
  44 |     """
  45 |     dataset = load_dataset(path=path, split=split)
  46 | 
  47 |     def process(sample):
  48 |         # Tokenize the full sequence (prompt + response)
  49 |         seq_token = tokenizer.encode(
  50 |             sample["question"] + sample["answer"] + tokenizer.eos_token
  51 |         )
  52 |         prompt_token = tokenizer.encode(sample["question"])
  53 |         # Loss mask: 0 for prompt, 1 for response
  54 |         loss_mask = [0] * len(prompt_token) + [1] * (len(seq_token) - len(prompt_token))
  55 |         return {"input_ids": seq_token, "loss_mask": loss_mask}
  56 | 
  57 |     dataset = dataset.map(process).remove_columns(["question", "answer"])
  58 | 
  59 |     if max_length is not None:
  60 |         dataset = dataset.filter(lambda x: len(x["input_ids"]) <= max_length)
  61 | 
  62 |     return dataset
  63 | 
  64 | 
  65 | def get_<name>_rl_dataset(
  66 |     path: str,
  67 |     split: str,
  68 |     tokenizer,
  69 |     max_length: int | None = None,
  70 | ) -> Dataset:
  71 |     """Load dataset for RL training.
  72 | 
  73 |     Args:
  74 |         path: Path to dataset
  75 |         split: Dataset split
  76 |         tokenizer: Tokenizer for length filtering
  77 |         max_length: Maximum sequence length
  78 | 
  79 |     Returns:
  80 |         HuggingFace Dataset with prompts and answers for reward computation
  81 |     """
  82 |     dataset = load_dataset(path=path, split=split)
  83 | 
  84 |     def process(sample):
  85 |         messages = [
  86 |             {
  87 |                 "role": "user",
  88 |                 "content": sample["question"],
  89 |             }
  90 |         ]
  91 |         return {"messages": messages, "answer": sample["answer"]}
  92 | 
  93 |     dataset = dataset.map(process).remove_columns(["question"])
  94 | 
  95 |     if max_length is not None:
  96 | 
  97 |         def filter_length(sample):
  98 |             content = sample["messages"][0]["content"]
  99 |             tokens = tokenizer.encode(content)
 100 |             return len(tokens) <= max_length
 101 | 
 102 |         dataset = dataset.filter(filter_length)
 103 | 
 104 |     return dataset
 105 | ```
 106 | 
 107 | ### Step 2: Register in __init__.py
 108 | 
 109 | Update `areal/dataset/__init__.py`:
 110 | 
 111 | ```python
 112 | # Add to VALID_DATASETS
 113 | VALID_DATASETS = [
 114 |     # ... existing datasets
 115 |     "<name>",
 116 | ]
 117 | 
 118 | # Add to _get_custom_dataset function
 119 | def _get_custom_dataset(name: str, ...):
 120 |     # ... existing code
 121 |     elif name == "<name>":
 122 |         from areal.dataset.<name> import get_<name>_sft_dataset, get_<name>_rl_dataset
 123 |         if dataset_type == "sft":
 124 |             return get_<name>_sft_dataset(path, split, max_length, tokenizer)
 125 |         else:
 126 |             return get_<name>_rl_dataset(path, split, max_length, tokenizer)
 127 | ```
 128 | 
 129 | ### Step 3: Add Config (Optional)
 130 | 
 131 | If the dataset needs special configuration, add to `areal/api/cli_args.py`:
 132 | 
 133 | ```python
 134 | @dataclass
 135 | class TrainDatasetConfig:
 136 |     # ... existing fields
 137 |     <name>_specific_field: Optional[str] = None
 138 | ```
 139 | 
 140 | ### Step 4: Add Tests
 141 | 
 142 | Create `tests/test_<name>_dataset.py`:
 143 | 
 144 | ```python
 145 | import pytest
 146 | from areal.dataset.<name> import get_<name>_sft_dataset, get_<name>_rl_dataset
 147 | 
 148 | def test_sft_dataset_loads(tokenizer):
 149 |     dataset = get_<name>_sft_dataset("path/to/data", split="train", tokenizer=tokenizer)
 150 |     assert len(dataset) > 0
 151 |     assert "input_ids" in dataset.column_names
 152 |     assert "loss_mask" in dataset.column_names
 153 | 
 154 | def test_rl_dataset_loads(tokenizer):
 155 |     dataset = get_<name>_rl_dataset("path/to/data", split="train", tokenizer=tokenizer)
 156 |     assert len(dataset) > 0
 157 |     assert "messages" in dataset.column_names
 158 |     assert "answer" in dataset.column_names
 159 | ```
 160 | 
 161 | ## Reference Implementations
 162 | 
 163 | | Dataset    | File                               | Description              |
 164 | | ---------- | ---------------------------------- | ------------------------ |
 165 | | GSM8K      | `areal/dataset/gsm8k.py`           | Math word problems       |
 166 | | Geometry3K | `areal/dataset/geometry3k.py`      | Geometry problems        |
 167 | | CLEVR      | `areal/dataset/clevr_count_70k.py` | Visual counting          |
 168 | | HH-RLHF    | `areal/dataset/hhrlhf.py`          | Helpfulness/Harmlessness |
 169 | | TORL       | `areal/dataset/torl_data.py`       | Tool-use RL              |
 170 | 
 171 | ## Required Fields
 172 | 
 173 | ### SFT Dataset
 174 | 
 175 | ```python
 176 | {
 177 |     "messages": [
 178 |         {"role": "user", "content": "..."},
 179 |         {"role": "assistant", "content": "..."},
 180 |     ]
 181 | }
 182 | ```
 183 | 
 184 | ### RL Dataset
 185 | 
 186 | ```python
 187 | {
 188 |     "messages": [
 189 |         {"role": "user", "content": "..."},
 190 |     ],
 191 |     "answer": "ground_truth_for_reward",
 192 |     # Optional metadata for reward function
 193 | }
 194 | ```
 195 | 
 196 | ## Common Mistakes
 197 | 
 198 | - ❌ Returning `List[Dict]` instead of HuggingFace `Dataset`
 199 | - ❌ Using Python loops instead of `dataset.map()`/`filter()`
 200 | - ❌ Missing `"messages"` field for RL datasets
 201 | - ❌ Wrong message format (should be list of dicts with `role` and `content`)
 202 | - ❌ Not registering in `__init__.py`
 203 | 
 204 | ______________________________________________________________________
 205 | 
 206 | <!--
 207 | ================================================================================
 208 |                             MAINTAINER GUIDE
 209 | ================================================================================
 210 | 
 211 | Location: .claude/skills/add-dataset/SKILL.md
 212 | Invocation: /add-dataset <name>
 213 | 
 214 | ## Purpose
 215 | 
 216 | Step-by-step guide for adding new dataset loaders.
 217 | 
 218 | ## How to Update
 219 | 
 220 | ### When Dataset API Changes
 221 | 1. Update the code templates
 222 | 2. Update required fields section
 223 | 3. Update registration example
 224 | 
 225 | ### When New Dataset Types Added
 226 | 1. Add to "Reference Implementations" table
 227 | 2. Add any new required fields
 228 | 
 229 | ================================================================================
 230 | -->
```


---
## .claude/skills/add-reward/SKILL.md

```
   1 | ---
   2 | name: add-reward
   3 | description: Guide for adding a new reward function to AReaL. Use when user wants to create a reward function.
   4 | ---
   5 | 
   6 | # Add Reward
   7 | 
   8 | Add a new reward function to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a reward function?"
  15 | - User wants to implement custom rewards
  16 | - User mentions reward computation
  17 | 
  18 | ## Step-by-Step Guide
  19 | 
  20 | ### Step 1: Create Reward File
  21 | 
  22 | Create `areal/reward/<name>.py`:
  23 | 
  24 | ```python
  25 | from typing import Any
  26 | 
  27 | from areal.utils import logging
  28 | 
  29 | logger = logging.getLogger("MyReward")
  30 | 
  31 | 
  32 | def <name>_reward_fn(
  33 |     prompt: str,
  34 |     completions: str,
  35 |     prompt_ids,
  36 |     completion_ids,
  37 |     answer: str | None = None,
  38 |     **kwargs: Any,
  39 | ) -> float:
  40 |     """Compute reward for a single completion.
  41 | 
  42 |     Args:
  43 |         prompt: Prompt string
  44 |         completions: Completion string (model output)
  45 |         prompt_ids: Tokenized prompt IDs
  46 |         completion_ids: Tokenized completion IDs
  47 |         answer: Ground truth answer from dataset (optional)
  48 |         **kwargs: Additional data from dataset
  49 | 
  50 |     Returns:
  51 |         Reward value (float), typically 0.0 or 1.0
  52 |     """
  53 |     try:
  54 |         # Extract answer from completion
  55 |         extracted = _extract_answer(completions)
  56 | 
  57 |         # Compare with ground truth
  58 |         if answer is not None and extracted == str(answer):
  59 |             return 1.0
  60 |         return 0.0
  61 |     except Exception:
  62 |         logger.warning("Exception in reward computation", exc_info=True)
  63 |         return 0.0
  64 | 
  65 | 
  66 | def _extract_answer(completion: str) -> str:
  67 |     """Extract the answer from a completion string.
  68 | 
  69 |     Implement your extraction logic here.
  70 |     """
  71 |     # Example: Extract content from \boxed{}
  72 |     import re
  73 | 
  74 |     match = re.search(r"\\boxed\{([^}]+)\}", completion)
  75 |     if match:
  76 |         return match.group(1).strip()
  77 |     return completion.strip()
  78 | ```
  79 | 
  80 | ### Step 2: Register in __init__.py
  81 | 
  82 | Update `areal/reward/__init__.py`:
  83 | 
  84 | ```python
  85 | # Add to VALID_REWARD_FN
  86 | VALID_REWARD_FN = [
  87 |     # ... existing reward functions
  88 |     "<name>",
  89 | ]
  90 | 
  91 | # Add to get_reward_fn function
  92 | def get_reward_fn(name: str, **kwargs):
  93 |     # ... existing code
  94 |     elif name == "<name>":
  95 |         from areal.reward.<name> import <name>_reward_fn
  96 |         return <name>_reward_fn
  97 | ```
  98 | 
  99 | ### Step 3: Handle Blocking Operations
 100 | 
 101 | If your reward function uses blocking operations (e.g., API calls, model inference), the
 102 | workflow will wrap it with `AsyncRewardWrapper`:
 103 | 
 104 | ```python
 105 | # In your workflow
 106 | from areal.reward import AsyncRewardWrapper
 107 | 
 108 | self.reward_fn = AsyncRewardWrapper(reward_fn)
 109 | 
 110 | # Then call it asynchronously
 111 | rewards = await self.reward_fn(prompt, completions, **data)
 112 | ```
 113 | 
 114 | ### Step 4: Add Tests
 115 | 
 116 | Create `tests/test_<name>_reward.py`:
 117 | 
 118 | ```python
 119 | import pytest
 120 | from areal.reward.<name> import <name>_reward_fn
 121 | 
 122 | def test_reward_correct_answer():
 123 |     reward = <name>_reward_fn(
 124 |         prompt="What is 2+2?",
 125 |         completions="The answer is \\boxed{4}",
 126 |         prompt_ids=None,
 127 |         completion_ids=None,
 128 |         answer="4",
 129 |     )
 130 |     assert reward == 1.0
 131 | 
 132 | def test_reward_wrong_answer():
 133 |     reward = <name>_reward_fn(
 134 |         prompt="What is 2+2?",
 135 |         completions="The answer is \\boxed{5}",
 136 |         prompt_ids=None,
 137 |         completion_ids=None,
 138 |         answer="4",
 139 |     )
 140 |     assert reward == 0.0
 141 | ```
 142 | 
 143 | ## Reference Implementations
 144 | 
 145 | | Reward     | File                              | Description                  |
 146 | | ---------- | --------------------------------- | ---------------------------- |
 147 | | GSM8K      | `areal/reward/gsm8k.py`           | Math answer verification     |
 148 | | Geometry3K | `areal/reward/geometry3k.py`      | Geometry answer verification |
 149 | | CLEVR      | `areal/reward/clevr_count_70k.py` | Counting verification        |
 150 | | MathVerify | `areal/reward/math_verify.py`     | General math verification    |
 151 | 
 152 | ## Function Signature
 153 | 
 154 | All reward functions must follow this signature:
 155 | 
 156 | ```python
 157 | def reward_fn(
 158 |     prompt: str,               # Input prompt string
 159 |     completions: str,          # Model completion string
 160 |     prompt_ids,                # Tokenized prompt
 161 |     completion_ids,            # Tokenized completion
 162 |     **kwargs: Any,             # Additional data from dataset (e.g., answer)
 163 | ) -> float:                    # Reward value (typically 0.0 or 1.0)
 164 | ```
 165 | 
 166 | **Note**: The reward function is called once per sample. Batching is handled by
 167 | `AsyncRewardWrapper` in the workflow.
 168 | 
 169 | ## Key Requirements
 170 | 
 171 | 1. **Deterministic**: Same inputs should produce same outputs
 172 | 1. **Return float**: Output is a single float value per sample
 173 | 1. **No blocking in async context**: Use `AsyncRewardWrapper` if needed
 174 | 1. **Logging**: Use `areal.utils.logging`, not `print`
 175 | 1. **Handle exceptions**: Return 0.0 on error, don't raise
 176 | 
 177 | ## Common Mistakes
 178 | 
 179 | - ❌ Returning a tensor instead of a float
 180 | - ❌ Expecting batched inputs (reward is called per sample)
 181 | - ❌ Non-deterministic behavior
 182 | - ❌ Blocking operations without `AsyncRewardWrapper`
 183 | - ❌ Raising exceptions instead of returning 0.0
 184 | 
 185 | ______________________________________________________________________
 186 | 
 187 | <!--
 188 | ================================================================================
 189 |                             MAINTAINER GUIDE
 190 | ================================================================================
 191 | 
 192 | Location: .claude/skills/add-reward/SKILL.md
 193 | Invocation: /add-reward <name>
 194 | 
 195 | ## Purpose
 196 | 
 197 | Step-by-step guide for adding new reward functions.
 198 | 
 199 | ## How to Update
 200 | 
 201 | ### When Reward API Changes
 202 | 1. Update the function signature section
 203 | 2. Update the code template
 204 | 3. Update key requirements
 205 | 
 206 | ### When New Reward Patterns Emerge
 207 | 1. Add to "Reference Implementations" table
 208 | 2. Add examples for new patterns
 209 | 
 210 | ================================================================================
 211 | -->
```


---
## .claude/skills/add-unit-tests/SKILL.md

```
   1 | ---
   2 | name: add-unit-tests
   3 | description: Guide for adding unit tests to AReaL. Use when user wants to add tests for new functionality or increase test coverage.
   4 | ---
   5 | 
   6 | # Add Unit Tests
   7 | 
   8 | Add unit tests to AReaL following the project's testing conventions.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add tests?"
  15 | - User wants to increase test coverage
  16 | - User needs to write tests for new functionality
  17 | - User wants to understand AReaL testing patterns
  18 | 
  19 | ## Step-by-Step Guide
  20 | 
  21 | ### Step 1: Understand Test Types
  22 | 
  23 | AReaL has two main test categories:
  24 | 
  25 | | Test Type             | Purpose                            | Location Pattern                   | How It Runs                                |
  26 | | --------------------- | ---------------------------------- | ---------------------------------- | ------------------------------------------ |
  27 | | **Unit Tests**        | Test individual functions/modules  | `tests/test_<module>_<feature>.py` | Directly via pytest                        |
  28 | | **Distributed Tests** | Test distributed/parallel behavior | `tests/torchrun/run_*.py`          | Via torchrun (called by pytest subprocess) |
  29 | 
  30 | **Note**: All tests are invoked via pytest. Distributed tests use `torchrun` but are
  31 | still called from pytest test files.
  32 | 
  33 | ### Step 2: Create Test File Structure
  34 | 
  35 | Create test file with naming convention: `test_<module>_<feature>.py`
  36 | 
  37 | ```python
  38 | import pytest
  39 | import torch
  40 | 
  41 | # Import the module to test
  42 | from areal.dataset.gsm8k import get_gsm8k_sft_dataset
  43 | from tests.utils import get_dataset_path  # Optional test utilities
  44 | # For mocking tokenizer: from unittest.mock import MagicMock
  45 | ```
  46 | 
  47 | ### Step 3: Write Test Functions
  48 | 
  49 | Follow Arrange-Act-Assert pattern:
  50 | 
  51 | ```python
  52 | def test_function_under_condition_returns_expected():
  53 |     """Test that function returns expected value under condition."""
  54 |     # Arrange
  55 |     input_data = 5
  56 |     expected_output = 10
  57 | 
  58 |     # Act
  59 |     result = function_under_test(input_data)
  60 | 
  61 |     # Assert
  62 |     assert result == expected_output
  63 | ```
  64 | 
  65 | ### Step 4: Add Pytest Markers and CI Strategy
  66 | 
  67 | Use appropriate pytest markers:
  68 | 
  69 | | Marker                                  | When to Use                                                  |
  70 | | --------------------------------------- | ------------------------------------------------------------ |
  71 | | `@pytest.mark.slow`                     | Test takes > 10 seconds (excluded from CI by default)        |
  72 | | `@pytest.mark.ci`                       | Slow test that must run in CI (use with `@pytest.mark.slow`) |
  73 | | `@pytest.mark.asyncio`                  | Async test functions                                         |
  74 | | `@pytest.mark.skipif(cond, reason=...)` | Conditional skip                                             |
  75 | | `@pytest.mark.parametrize(...)`         | Parameterized tests                                          |
  76 | 
  77 | **CI Test Strategy**:
  78 | 
  79 | - `@pytest.mark.slow`: Excluded from CI by default (CI runs `pytest -m "not slow"`)
  80 | - `@pytest.mark.slow` + `@pytest.mark.ci`: Slow but must run in CI
  81 | - No marker: Runs in CI (fast unit tests)
  82 | 
  83 | ```python
  84 | @pytest.mark.asyncio
  85 | async def test_async_function():
  86 |     result = await async_function()
  87 |     assert result == expected
  88 | 
  89 | @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
  90 | def test_gpu_feature():
  91 |     tensor = torch.tensor([1, 2, 3], device="cuda")
  92 |     # ... assertions
  93 | 
  94 | @pytest.mark.parametrize("batch_size", [1, 4, 16])
  95 | def test_with_parameters(batch_size):
  96 |     # Parameterized test
  97 | 
  98 | @pytest.mark.slow
  99 | def test_slow_function():
 100 |     # Excluded from CI by default
 101 | 
 102 | @pytest.mark.slow
 103 | @pytest.mark.ci
 104 | def test_slow_but_required_in_ci():
 105 |     # Slow but must run in CI
 106 | ```
 107 | 
 108 | ### Step 5: Mock Distributed Environment
 109 | 
 110 | For unit tests that need distributed mocks:
 111 | 
 112 | ```python
 113 | import torch.distributed as dist
 114 | 
 115 | def test_distributed_function(monkeypatch):
 116 |     monkeypatch.setattr(dist, "get_rank", lambda: 0)
 117 |     monkeypatch.setattr(dist, "get_world_size", lambda: 2)
 118 |     result = distributed_function()
 119 |     assert result == expected
 120 | ```
 121 | 
 122 | ### Step 6: Handle GPU Dependencies
 123 | 
 124 | Always skip gracefully when GPU unavailable:
 125 | 
 126 | ```python
 127 | CUDA_AVAILABLE = torch.cuda.is_available()
 128 | 
 129 | @pytest.mark.skipif(not CUDA_AVAILABLE, reason="CUDA not available")
 130 | def test_gpu_function():
 131 |     tensor = torch.tensor([1, 2, 3], device="cuda")
 132 |     # ... assertions
 133 | ```
 134 | 
 135 | ## Key Requirements (Based on testing.md)
 136 | 
 137 | ### Mocking Distributed
 138 | 
 139 | - Use `torch.distributed.fake_pg` for unit tests
 140 | - Mock `dist.get_rank()` and `dist.get_world_size()` explicitly
 141 | - Don't mock internals of FSDP/DTensor
 142 | 
 143 | ### GPU Test Constraints
 144 | 
 145 | - **Always skip gracefully** when GPU unavailable
 146 | - Clean up GPU memory: `torch.cuda.empty_cache()` in fixtures
 147 | - Use smallest possible model/batch for unit tests
 148 | 
 149 | ### Assertions
 150 | 
 151 | - Use `torch.testing.assert_close()` for tensor comparison
 152 | - Specify `rtol`/`atol` explicitly for numerical tests
 153 | - Avoid bare `assert tensor.equal()` - no useful error message
 154 | 
 155 | ## Reference Implementations
 156 | 
 157 | | Test File                        | Description                            | Key Patterns                                      |
 158 | | -------------------------------- | -------------------------------------- | ------------------------------------------------- |
 159 | | `tests/test_utils.py`            | Utility function tests                 | Fixtures, parametrized tests                      |
 160 | | `tests/test_examples.py`         | Integration tests with dataset loading | Dataset path resolution, success pattern matching |
 161 | | `tests/test_fsdp_engine_nccl.py` | Distributed tests                      | Torchrun integration                              |
 162 | 
 163 | ## Common Mistakes
 164 | 
 165 | - ❌ **Missing test file registration**: Ensure file follows `test_*.py` naming
 166 | - ❌ **GPU dependency without skip**: Always use `@pytest.mark.skipif` for GPU tests
 167 | - ❌ **Incorrect tensor comparisons**: Use `torch.testing.assert_close()` not
 168 |   `assert tensor.equal()`
 169 | - ❌ **Memory leaks in GPU tests**: Clean up with `torch.cuda.empty_cache()`
 170 | - ❌ **Mocking too much**: Don't mock FSDP/DTensor internals
 171 | - ❌ **Unclear test names**: Follow `test_<what>_<condition>_<expected>` pattern
 172 | - ❌ **No docstrings**: Add descriptive docstrings to test functions
 173 | 
 174 | ## Integration with Other Skills
 175 | 
 176 | This skill complements other AReaL development skills:
 177 | 
 178 | - **After `/add-dataset`**: Add tests for new dataset loaders
 179 | - **After `/add-workflow`**: Add tests for new workflows
 180 | - **After `/add-reward`**: Add tests for new reward functions
 181 | - **With `planner` agent**: Reference this skill when planning test implementation
 182 | 
 183 | ## Running Tests
 184 | 
 185 | ```bash
 186 | # First check GPU availability (many tests require GPU)
 187 | python -c "import torch; print('GPU available:', torch.cuda.is_available())"
 188 | 
 189 | # Run specific test file
 190 | uv run pytest tests/test_<name>.py
 191 | 
 192 | # Skip slow tests (CI default)
 193 | uv run pytest -m "not slow"
 194 | 
 195 | # Run with verbose output
 196 | uv run pytest -v
 197 | 
 198 | # Run distributed tests (requires torchrun and multi-GPU)
 199 | # Note: Usually invoked via pytest test files
 200 | torchrun --nproc_per_node=2 tests/torchrun/run_<test>.py
 201 | ```
 202 | 
 203 | <!--
 204 | ================================================================================
 205 |                             MAINTAINER GUIDE
 206 | ================================================================================
 207 | 
 208 | Location: .claude/skills/add-unit-tests/SKILL.md
 209 | Invocation: /add-unit-tests
 210 | 
 211 | ## Purpose
 212 | 
 213 | Step-by-step guide for adding unit tests to AReaL.
 214 | 
 215 | ## How to Update
 216 | 
 217 | ### When Testing Conventions Change
 218 | 1. Update "Key Requirements" section based on `testing.md`
 219 | 2. Update test examples to match new patterns
 220 | 3. Update reference implementations
 221 | 
 222 | ### When Test Types Need Update
 223 | 1. Update "Understand Test Types" table (currently two main types)
 224 | 2. Add new examples if needed
 225 | 3. Update common mistakes
 226 | 
 227 | ### Integration with Other Skills
 228 | Ensure references to other skills (`/add-dataset`, `/add-workflow`, `/add-reward`) remain accurate.
 229 | 
 230 | ================================================================================
 231 | -->
```


---
## .claude/skills/add-workflow/SKILL.md

```
   1 | ---
   2 | name: add-workflow
   3 | description: Guide for adding a new RolloutWorkflow to AReaL. Use when user wants to create a new workflow.
   4 | ---
   5 | 
   6 | # Add Workflow
   7 | 
   8 | Add a new RolloutWorkflow implementation to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a workflow?"
  15 | - User wants to create a new RolloutWorkflow
  16 | - User mentions implementing a custom rollout
  17 | 
  18 | ## Prerequisites
  19 | 
  20 | Before starting, ensure you understand:
  21 | 
  22 | - The workflow's purpose and requirements
  23 | - Input/output data format
  24 | - Reward function to use
  25 | 
  26 | ## Step-by-Step Guide
  27 | 
  28 | ### Step 1: Create Workflow File
  29 | 
  30 | Create `areal/workflow/<name>.py`:
  31 | 
  32 | ```python
  33 | import uuid
  34 | from typing import Any, Callable
  35 | 
  36 | import torch
  37 | 
  38 | from areal.api.cli_args import GenerationHyperparameters
  39 | from areal.api.engine_api import InferenceEngine
  40 | from areal.api.io_struct import ModelRequest, ModelResponse
  41 | from areal.api.reward_api import AsyncRewardWrapper
  42 | from areal.api.workflow_api import RolloutWorkflow
  43 | from areal.utils import logging
  44 | 
  45 | logger = logging.getLogger("MyWorkflow")
  46 | 
  47 | 
  48 | class MyWorkflow(RolloutWorkflow):
  49 |     """Description of your workflow."""
  50 | 
  51 |     def __init__(
  52 |         self,
  53 |         gconfig: GenerationHyperparameters,
  54 |         tokenizer,
  55 |         reward_fn: Callable,
  56 |     ):
  57 |         self.gconfig = gconfig.new_with_stop_and_pad_token_ids(tokenizer)
  58 |         self.tokenizer = tokenizer
  59 |         self.async_reward_fn = AsyncRewardWrapper(reward_fn)
  60 | 
  61 |     async def arun_episode(
  62 |         self,
  63 |         engine: InferenceEngine,
  64 |         data: dict[str, Any],
  65 |     ) -> dict[str, torch.Tensor]:
  66 |         """Run a single episode. MUST be async and non-blocking."""
  67 | 
  68 |         # 1. Prepare input_ids from data
  69 |         input_ids = self.tokenizer.apply_chat_template(
  70 |             data["messages"],
  71 |             tokenize=True,
  72 |             add_generation_prompt=True,
  73 |         )
  74 | 
  75 |         # 2. Build ModelRequest
  76 |         req = ModelRequest(
  77 |             rid=uuid.uuid4().hex,
  78 |             input_ids=list(input_ids),
  79 |             gconfig=self.gconfig.new(n_samples=1),
  80 |             tokenizer=self.tokenizer,
  81 |         )
  82 | 
  83 |         # 3. Generate completion (async)
  84 |         resp: ModelResponse = await engine.agenerate(req)
  85 | 
  86 |         # 4. Compute reward (async)
  87 |         prompt_str = self.tokenizer.decode(input_ids)
  88 |         completion_str = self.tokenizer.decode(resp.output_tokens)
  89 |         reward = await self.async_reward_fn(
  90 |             prompt_str,
  91 |             completion_str,
  92 |             resp.input_tokens,
  93 |             resp.output_tokens,
  94 |             **data,
  95 |         )
  96 | 
  97 |         # 5. Return results in expected format
  98 |         return {
  99 |             "input_ids": torch.tensor(resp.input_tokens),
 100 |             "output_ids": torch.tensor(resp.output_tokens),
 101 |             "reward": torch.tensor(reward),
 102 |         }
 103 | ```
 104 | 
 105 | ### Step 2: Register in __init__.py
 106 | 
 107 | Add to `areal/workflow/__init__.py`:
 108 | 
 109 | ```python
 110 | from areal.workflow.<name> import MyWorkflow
 111 | 
 112 | __all__ = [
 113 |     # ... existing exports
 114 |     "MyWorkflow",
 115 | ]
 116 | ```
 117 | 
 118 | ### Step 3: Update Entry Script
 119 | 
 120 | Update your training script to use the new workflow:
 121 | 
 122 | ```python
 123 | trainer.train(
 124 |     workflow="areal.workflow.<name>.MyWorkflow",
 125 |     # ... other args
 126 | )
 127 | ```
 128 | 
 129 | ### Step 4: Add Tests
 130 | 
 131 | Create `tests/test_<name>_workflow.py`:
 132 | 
 133 | ```python
 134 | import pytest
 135 | from areal.workflow.<name> import MyWorkflow
 136 | 
 137 | @pytest.mark.asyncio
 138 | async def test_workflow_basic():
 139 |     # Test basic functionality
 140 |     pass
 141 | ```
 142 | 
 143 | ## Reference Implementations
 144 | 
 145 | | Workflow           | File                            | Description                |
 146 | | ------------------ | ------------------------------- | -------------------------- |
 147 | | MultiTurnWorkflow  | `areal/workflow/multi_turn.py`  | Multi-turn conversation    |
 148 | | RLVRWorkflow       | `areal/workflow/rlvr.py`        | RL with verifiable rewards |
 149 | | VisionRLVRWorkflow | `areal/workflow/vision_rlvr.py` | Vision + RLVR              |
 150 | 
 151 | ## Key Requirements
 152 | 
 153 | 1. **Async**: `arun_episode` must be `async def` and non-blocking
 154 | 1. **No sync I/O**: Use `aiofiles` for file operations
 155 | 1. **Wrap rewards**: Use `AsyncRewardWrapper` for reward functions
 156 | 1. **Tensor format**: Output tensors should be `[batch, seq_len, ...]`
 157 | 1. **Use helpers**: `concat_padded_tensors` for combining outputs
 158 | 
 159 | ## Common Mistakes
 160 | 
 161 | - ❌ Using `open()` instead of `aiofiles.open()`
 162 | - ❌ Forgetting to `await` async calls
 163 | - ❌ Not wrapping reward function with `AsyncRewardWrapper`
 164 | - ❌ Wrong tensor shape conventions
 165 | 
 166 | ______________________________________________________________________
 167 | 
 168 | <!--
 169 | ================================================================================
 170 |                             MAINTAINER GUIDE
 171 | ================================================================================
 172 | 
 173 | Location: .claude/skills/add-workflow/SKILL.md
 174 | Invocation: /add-workflow <name>
 175 | 
 176 | ## Purpose
 177 | 
 178 | Step-by-step guide for adding new RolloutWorkflow implementations.
 179 | 
 180 | ## How to Update
 181 | 
 182 | ### When Workflow API Changes
 183 | 1. Update the code template in Step 1
 184 | 2. Update the required imports
 185 | 3. Update the method signature if changed
 186 | 
 187 | ### When New Patterns Emerge
 188 | 1. Add to "Reference Implementations" table
 189 | 2. Update "Key Requirements" if new requirements added
 190 | 
 191 | ================================================================================
 192 | -->
```


---
## .claude/skills/commit-conventions/SKILL.md

```
   1 | ---
   2 | name: commit-conventions
   3 | description: AReaL commit message conventions. MUST load on every git commit -- provides Conventional Commits format with scope inference from file paths.
   4 | ---
   5 | 
   6 | # Commit Conventions
   7 | 
   8 | Commit message conventions and scope inference rules for the AReaL repository.
   9 | 
  10 | ## When to Use
  11 | 
  12 | **ALWAYS load this skill when making any git commit in AReaL.** This includes:
  13 | 
  14 | - Direct commits (`git commit`)
  15 | - Commits during PR creation (`/create-pr`)
  16 | - Commits delegated via Agent tool with `skills: ["commit-conventions"]`
  17 | - Any agent workflow that produces a commit
  18 | 
  19 | ## Commit Message Format
  20 | 
  21 | ```
  22 | <type>(<scope>): <subject>
  23 | 
  24 | <body>
  25 | 
  26 | [Optional sections:]
  27 | Key changes:
  28 | - change 1
  29 | - change 2
  30 | 
  31 | Refs: #123, #456
  32 | ```
  33 | 
  34 | ## Type Selection
  35 | 
  36 | | Type       | When to Use                     |
  37 | | ---------- | ------------------------------- |
  38 | | `feat`     | New feature or capability       |
  39 | | `fix`      | Bug fix                         |
  40 | | `docs`     | Documentation only              |
  41 | | `refactor` | Code change without feature/fix |
  42 | | `test`     | Adding or fixing tests          |
  43 | | `chore`    | Build, deps, config changes     |
  44 | | `perf`     | Performance improvement         |
  45 | 
  46 | ## Scope Inference
  47 | 
  48 | Infer scope from the **primary** changed file paths:
  49 | 
  50 | | File Path Pattern                                            | Scope                          |
  51 | | ------------------------------------------------------------ | ------------------------------ |
  52 | | `areal/workflow/`                                            | `workflow`                     |
  53 | | `areal/engine/`                                              | `engine`                       |
  54 | | `areal/reward/`                                              | `reward`                       |
  55 | | `areal/dataset/`                                             | `dataset`                      |
  56 | | `areal/api/`                                                 | `api`                          |
  57 | | `areal/utils/`                                               | `utils`                        |
  58 | | `areal/infra/`                                               | `infra`                        |
  59 | | `areal/trainer/`                                             | `trainer`                      |
  60 | | `areal/models/`                                              | `models`                       |
  61 | | `areal/experimental/`                                        | `archon`                       |
  62 | | `docs/`                                                      | `docs`                         |
  63 | | `examples/`                                                  | `examples`                     |
  64 | | `AGENTS.md`, `.agents/`, `.claude/`, `.codex/`, `.opencode/` | `agents`                       |
  65 | | Multiple areas                                               | Omit scope or use broader term |
  66 | 
  67 | ## Rules
  68 | 
  69 | - **Subject**: imperative mood, ~50-72 chars, no trailing period
  70 | - **Body**: explain "why" not "what", wrap at 72 chars
  71 | - **Key changes**: bullet list of main modifications (for complex commits with 3+ files)
  72 | - **Refs**: reference issues/PRs if applicable
  73 | 
  74 | ## Examples
  75 | 
  76 | **Single file fix:**
  77 | 
  78 | ```
  79 | fix(reward): handle empty completion in gsm8k
  80 | 
  81 | Return 0 reward instead of raising exception when
  82 | completion string is empty after extraction.
  83 | ```
  84 | 
  85 | **Multi-file feature:**
  86 | 
  87 | ```
  88 | feat(engine): add CPU offload support to ArchonEngine
  89 | 
  90 | Enable torch_memory_saver for model offloading during
  91 | rollout phase to reduce GPU memory pressure.
  92 | 
  93 | Key changes:
  94 | - Add offload/onload methods to ArchonEngine
  95 | - Integrate with weight update flow
  96 | - Handle ROCm compatibility
  97 | ```
  98 | 
  99 | **Docs only:**
 100 | 
 101 | ```
 102 | docs: update algorithm comparison table
 103 | 
 104 | Add SAPO and GSPO to the algorithm family documentation
 105 | with configuration examples.
 106 | ```
 107 | 
 108 | **Agent/tooling changes:**
 109 | 
 110 | ```
 111 | chore(agents): port review-pr command to OpenCode
 112 | 
 113 | Add OpenCode-native commands with task() category
 114 | delegation instead of hardcoded model names.
 115 | 
 116 | Key changes:
 117 | - Create .opencode/command/ with review-pr, create-pr
 118 | - Replace Opus/Sonnet/Haiku with deep/unspecified-high/quick
 119 | - Add expert subagent consultation patterns
 120 | ```
 121 | 
 122 | ______________________________________________________________________
 123 | 
 124 | <!--
 125 | ================================================================================
 126 |                             MAINTAINER GUIDE
 127 | ================================================================================
 128 | 
 129 | Location: .claude/skills/commit-conventions/SKILL.md
 130 | Invocation: Automatically loaded on every git commit via load_skills
 131 | 
 132 | ## Purpose
 133 | 
 134 | Provides Conventional Commits format with AReaL-specific scope inference
 135 | from file paths. Unlike other skills, this one is NOT user-triggered --
 136 | it is loaded by the system/agent on every commit operation.
 137 | 
 138 | ## How to Update
 139 | 
 140 | ### When New Modules Are Added
 141 | 1. Add the file path pattern and scope to the "Scope Inference" table
 142 | 2. Keep table sorted by areal/ subpackages first, then top-level dirs
 143 | 
 144 | ### When Commit Types Change
 145 | 1. Update the "Type Selection" table
 146 | 2. Add/update examples to illustrate the new type
 147 | 
 148 | ### When Adding Examples
 149 | 1. Each example should demonstrate a distinct commit pattern
 150 | 2. Keep examples realistic -- use actual AReaL module names
 151 | 3. Show both subject-only and subject+body+key-changes variants
 152 | 
 153 | ### Important Design Decisions
 154 | - This skill is ALWAYS loaded (not optional) -- keep it concise to
 155 |   minimize token overhead on every commit
 156 | - Scope inference is path-based, not content-based -- simpler and
 157 |   more deterministic
 158 | - "Multiple areas" -> omit scope rather than invent a new one
 159 | 
 160 | ================================================================================
 161 | -->
```


---
## .claude/skills/debug-distributed/SKILL.md

```
   1 | ---
   2 | name: debug-distributed
   3 | description: Guide for debugging distributed training issues in AReaL. Use when user encounters hangs, wrong results, OOM, or communication errors.
   4 | ---
   5 | 
   6 | # Debug Distributed Training
   7 | 
   8 | Debugging guide for distributed training issues in AReaL (FSDP2, TP, CP, EP).
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - Training hangs or deadlocks
  15 | - Results differ across ranks or are numerically wrong
  16 | - OOM errors in distributed settings
  17 | - NCCL/communication errors or device mesh issues
  18 | 
  19 | ## Debugging Principles
  20 | 
  21 | ### Minimal Reproduction
  22 | 
  23 | **Always follow the minimal demo principle**: Reproduce with the least amount of code to
  24 | narrow down the issue faster.
  25 | 
  26 | ```python
  27 | # Bad: Debug in full training loop
  28 | # Good: Create minimal script
  29 | import torch
  30 | import torch.distributed as dist
  31 | 
  32 | dist.init_process_group("nccl")
  33 | rank = dist.get_rank()
  34 | 
  35 | # Reproduce the exact operation that fails
  36 | tensor = torch.ones(10).cuda()
  37 | dist.all_reduce(tensor)  # <-- Isolate the failing op
  38 | print(f"Rank {rank}: {tensor}")
  39 | ```
  40 | 
  41 | **Reduction strategy:**
  42 | 
  43 | 1. Remove unrelated model components
  44 | 1. Use small tensor sizes
  45 | 1. Reduce world_size to minimum (e.g., 2 GPUs)
  46 | 1. Remove torch.compile if possible
  47 | 1. Disable activation checkpointing
  48 | 
  49 | ## Step-by-Step Debugging Guide
  50 | 
  51 | ### 1. Hang Debugging (Deadlocks, Synchronization)
  52 | 
  53 | **Environment Variables for Debugging**:
  54 | 
  55 | ```bash
  56 | # Full debug logging
  57 | export TORCH_DISTRIBUTED_DEBUG=DETAIL
  58 | export NCCL_DEBUG=INFO
  59 | export NCCL_DEBUG_SUBSYS=ALL
  60 | 
  61 | # torch.compile debugging
  62 | export TORCH_LOGS="+dynamo,recompiles"
  63 | export TORCHDYNAMO_VERBOSE=1
  64 | ```
  65 | 
  66 | **Dump Call Stack with py-spy** (for hung processes):
  67 | 
  68 | ```bash
  69 | # Find process IDs
  70 | ps aux | grep python
  71 | 
  72 | # Dump call stack of specific rank
  73 | py-spy dump --pid <PID>
  74 | 
  75 | # Record flame graph for performance analysis
  76 | py-spy record -o profile.svg --pid <PID> --duration 30
  77 | ```
  78 | 
  79 | **Common Causes**:
  80 | 
  81 | 1. **Mismatched Collectives**: One rank calls `all_reduce`, another doesn't.
  82 | 1. **Wrong Process Group**: Using wrong group for collective.
  83 | 1. **Tensor Shape Mismatch**: Different shapes across ranks.
  84 | 
  85 | **Debug Steps**:
  86 | 
  87 | ```python
  88 | # Verify group membership
  89 | mesh = parallel_dims.get_mesh("dp_shard_cp")
  90 | group = mesh.get_group()
  91 | print(f"Rank {dist.get_rank()}: group size = {dist.get_world_size(group)}")
  92 | 
  93 | # Print shapes on all ranks
  94 | print(f"Rank {dist.get_rank()}: tensor.shape = {tensor.shape}")
  95 | dist.barrier()
  96 | ```
  97 | 
  98 | **Timeout Adjustment** (for debugging only):
  99 | 
 100 | ```python
 101 | from areal.engine.core.distributed import patch_dist_group_timeout
 102 | from datetime import timedelta
 103 | patch_dist_group_timeout(timedelta(minutes=30))
 104 | ```
 105 | 
 106 | ### 2. Wrong Results (Gradient, Reduction Issues)
 107 | 
 108 | **Check DTensor Placements**:
 109 | 
 110 | ```python
 111 | from torch.distributed.tensor import DTensor
 112 | if isinstance(param, DTensor):
 113 |     print(f"Param {name}: placements={param.placements}, mesh={param.device_mesh}")
 114 | ```
 115 | 
 116 | **Verify Gradient Reduction**:
 117 | 
 118 | ```python
 119 | for name, param in model.named_parameters():
 120 |     if param.grad is not None:
 121 |         print(f"Rank {dist.get_rank()}: {name} grad_sum = {param.grad.sum().item()}")
 122 | ```
 123 | 
 124 | ### 3. OOM Issues (Memory, Sharding)
 125 | 
 126 | **Check Memory Usage**:
 127 | 
 128 | ```python
 129 | print(f"Rank {dist.get_rank()}: "
 130 |       f"allocated={torch.cuda.memory_allocated()/1e9:.2f}GB, "
 131 |       f"reserved={torch.cuda.memory_reserved()/1e9:.2f}GB")
 132 | ```
 133 | 
 134 | **Check FSDP Coverage**:
 135 | 
 136 | ```python
 137 | for name, param in model.named_parameters():
 138 |     is_dtensor = isinstance(param, DTensor)
 139 |     print(f"{name}: is_dtensor={is_dtensor}, shape={param.shape}")
 140 | ```
 141 | 
 142 | ### 4. Communication Errors
 143 | 
 144 | | Error                     | Cause                | Solution                           |
 145 | | ------------------------- | -------------------- | ---------------------------------- |
 146 | | `NCCL WARN Cuda failure`  | GPU communication    | Check NCCL version, GPU topology   |
 147 | | `RuntimeError: Timed out` | Rank synchronization | Increase timeout, check code paths |
 148 | | `Invalid device mesh`     | Mesh configuration   | Verify world_size = dp * tp * cp   |
 149 | 
 150 | ## Debugging Tools
 151 | 
 152 | ### Environment Variables Reference
 153 | 
 154 | | Variable                          | Purpose                                |
 155 | | --------------------------------- | -------------------------------------- |
 156 | | `TORCH_DISTRIBUTED_DEBUG=DETAIL`  | Detailed distributed logging           |
 157 | | `NCCL_DEBUG=INFO`                 | NCCL communication logging             |
 158 | | `NCCL_DEBUG_SUBSYS=ALL`           | All NCCL subsystems                    |
 159 | | `TORCH_LOGS="+dynamo,recompiles"` | torch.compile logging                  |
 160 | | `TORCHDYNAMO_VERBOSE=1`           | Dynamo verbose output                  |
 161 | | `CUDA_LAUNCH_BLOCKING=1`          | Synchronous CUDA (slow, for debugging) |
 162 | 
 163 | ### py-spy for Call Stack Analysis
 164 | 
 165 | ```bash
 166 | # Install
 167 | pip install py-spy
 168 | 
 169 | # Dump call stack of hung process
 170 | py-spy dump --pid <PID>
 171 | 
 172 | # Dump all Python processes
 173 | pgrep -f python | xargs -I {} py-spy dump --pid {}
 174 | 
 175 | # Record flame graph
 176 | py-spy record -o profile.svg --pid <PID> --duration 30
 177 | ```
 178 | 
 179 | ### Rank-Conditional Printing
 180 | 
 181 | ```python
 182 | def print_all_ranks(msg):
 183 |     for r in range(dist.get_world_size()):
 184 |         if dist.get_rank() == r:
 185 |             print(f"[Rank {r}] {msg}")
 186 |         dist.barrier()
 187 | ```
 188 | 
 189 | ### Check Device Mesh
 190 | 
 191 | ```python
 192 | def debug_mesh(parallel_dims):
 193 |     mesh = parallel_dims.world_mesh
 194 |     for dim_name in mesh.mesh_dim_names:
 195 |         submesh = parallel_dims.get_mesh(dim_name)
 196 |         if submesh:
 197 |             print(f"Rank {dist.get_rank()}: {dim_name} size={submesh.size()}")
 198 | ```
 199 | 
 200 | ### Validate Tensor Consistency
 201 | 
 202 | ```python
 203 | def check_tensor_consistency(tensor, name, group=None):
 204 |     local_sum = tensor.sum().item()
 205 |     tensor_sums = [None] * dist.get_world_size(group)
 206 |     dist.all_gather_object(tensor_sums, local_sum, group=group)
 207 |     if dist.get_rank() == 0 and len(set(tensor_sums)) > 1:
 208 |         print(f"WARNING: {name} inconsistent: {tensor_sums}")
 209 | ```
 210 | 
 211 | ## Key Files Reference
 212 | 
 213 | | Component       | File                                                          |
 214 | | --------------- | ------------------------------------------------------------- |
 215 | | Parallel Dims   | `areal/experimental/models/archon/parallel_dims.py`           |
 216 | | Expert Parallel | `areal/experimental/models/archon/expert_parallel.py`         |
 217 | | Ulysses (CP)    | `areal/experimental/models/archon/ulysses.py`                 |
 218 | | FSDP/TP Apply   | `areal/experimental/models/archon/qwen2/infra/parallelize.py` |
 219 | 
 220 | ______________________________________________________________________
 221 | 
 222 | <!--
 223 | ================================================================================
 224 |                             MAINTAINER GUIDE
 225 | ================================================================================
 226 | 
 227 | Location: .claude/skills/debug-distributed/SKILL.md
 228 | Invocation: /debug-distributed
 229 | 
 230 | ## Purpose
 231 | 
 232 | Debugging guide for distributed training issues.
 233 | Covers FSDP2, Tensor Parallelism, Context Parallelism, and Expert Parallelism.
 234 | 
 235 | ## How to Update
 236 | 
 237 | ### When Adding New Parallelism Features
 238 | 1. Add section for the parallelism type
 239 | 2. Document common error patterns and debugging snippets
 240 | 
 241 | ### When PyTorch Distributed APIs Change
 242 | 1. Update DTensor/DeviceMesh examples
 243 | 2. Update environment variable references
 244 | 
 245 | ### When New Error Patterns Emerge
 246 | 1. Add to "Common Errors and Solutions" table
 247 | 2. Reference relevant source files
 248 | 
 249 | ================================================================================
 250 | -->
```


---
## .opencode/skills/add-archon-model/SKILL.md

```
   1 | ---
   2 | name: add-archon-model
   3 | description: Guide for adding a new model to the Archon engine. Use when user wants to add support for a new HuggingFace model architecture in ArchonEngine.
   4 | ---
   5 | 
   6 | # Add Archon Model
   7 | 
   8 | Add support for a new HuggingFace model architecture in the Archon training engine.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a model to Archon?"
  15 | - User wants to support a new model family (e.g., Llama, Mistral, DeepSeek) in
  16 |   ArchonEngine
  17 | - User mentions adding a new `ModelSpec` or model type for Archon
  18 | 
  19 | ## Prerequisites
  20 | 
  21 | Before starting, ensure:
  22 | 
  23 | - The target model is available on HuggingFace (has `config.json` with `model_type`)
  24 | - You know the HuggingFace model ID (e.g., `meta-llama/Llama-3-8B`)
  25 | - The model uses a standard transformer architecture (decoder-only)
  26 | 
  27 | ## Step-by-Step Guide
  28 | 
  29 | ### Step 1: Analyze the Target Model Architecture
  30 | 
  31 | Read the HuggingFace model's source code to extract key architecture information.
  32 | 
  33 | **Action**: Fetch and analyze the model's HuggingFace configuration and modeling files.
  34 | 
  35 | 1. Read the model's `config.json` (via `AutoConfig.from_pretrained`) to identify:
  36 | 
  37 |    - `model_type` string (this is the key used for registry lookup)
  38 |    - All architecture hyperparameters (hidden_size, num_layers, etc.)
  39 |    - Any model-specific fields (e.g., `qk_norm`, `attention_bias`, MoE fields)
  40 | 
  41 | 1. Read the HuggingFace `modeling_*.py` source to identify:
  42 | 
  43 |    - **Attention variant**: Does it have Q/K norm? Attention bias? Sliding window?
  44 |      Multi-latent attention?
  45 |    - **FFN variant**: SwiGLU (gate_proj + up_proj + down_proj)? GeGLU? Standard MLP?
  46 |    - **MoE support**: Does it have MoE layers? What router type? Shared experts?
  47 |    - **RoPE variant**: Standard RoPE? YaRN? NTK-aware scaling? What is the inv_freq
  48 |      formula?
  49 |    - **Normalization**: RMSNorm or LayerNorm? Pre-norm or post-norm? Elementwise affine?
  50 |    - **Weight tying**: Does `tie_word_embeddings` appear in config?
  51 |    - **State dict key names**: What are the HF weight key naming conventions?
  52 | 
  53 | 1. Summarize findings in a checklist like:
  54 | 
  55 | ```
  56 | Target model: <name>
  57 | HF model_type: "<model_type>" (and variants like "<model_type>_moe" if applicable)
  58 | Attention: [standard GQA / with QK norm / with bias / sliding window / ...]
  59 | FFN: [SwiGLU / GeGLU / standard MLP / ...]
  60 | MoE: [no / yes - num_experts, top_k, shared_experts]
  61 | RoPE: [standard / YaRN / NTK-aware / ...]
  62 | Norm: [RMSNorm / LayerNorm] with [pre-norm / post-norm]
  63 | Weight tying: [yes / no]
  64 | ```
  65 | 
  66 | ### Step 2: Select the Reference Model
  67 | 
  68 | Choose the closest existing implementation as a starting point:
  69 | 
  70 | | Target characteristics               | Reference | Why                                     |
  71 | | ------------------------------------ | --------- | --------------------------------------- |
  72 | | Dense-only, standard GQA, no QK norm | `qwen2`   | Simplest baseline, pure dense           |
  73 | | Has QK norm, or has MoE support      | `qwen3`   | Supports QK norm + MoE + shared experts |
  74 | 
  75 | **Action**: Copy the reference model directory as the starting point:
  76 | 
  77 | ```
  78 | areal/experimental/models/archon/<model>/
  79 |   __init__.py
  80 |   spec.py
  81 |   model/
  82 |     args.py
  83 |     model.py
  84 |     rope.py
  85 |     state_dict_adapter.py
  86 |   infra/
  87 |     parallelize.py
  88 | ```
  89 | 
  90 | ### Step 3: Implement `args.py`
  91 | 
  92 | Adapt `<Model>ModelArgs` to match the target model's HuggingFace config fields.
  93 | 
  94 | **Key changes from reference**:
  95 | 
  96 | 1. Update the `@dataclass` fields to match the target model's hyperparameters:
  97 | 
  98 |    - Field names should use Archon conventions (`dim`, `n_layers`, `n_heads`,
  99 |      `n_kv_heads`, `vocab_size`, `head_dim`, `hidden_dim`, `norm_eps`, `rope_theta`,
 100 |      etc.)
 101 |    - Default values should match the smallest variant of the target model
 102 |    - Add model-specific fields (e.g., `attention_bias`, `qk_norm`, `sliding_window`)
 103 | 
 104 | 1. Update `from_hf_config()` to correctly map HuggingFace config attributes:
 105 | 
 106 |    - Use `getattr(hf_config, "field_name", default)` for optional fields
 107 |    - Handle variant-specific fields (e.g., MoE fields only present in MoE variants)
 108 |    - The method must return an instance of the model args class
 109 | 
 110 | **Critical**: Verify every field mapping against the HF model's `config.json`. Incorrect
 111 | mappings here cause silent errors downstream.
 112 | 
 113 | **Base class contract** (`BaseModelArgs`):
 114 | 
 115 | ```python
 116 | @dataclass
 117 | class <Model>ModelArgs(BaseModelArgs):
 118 |     # ... model-specific fields ...
 119 | 
 120 |     @classmethod
 121 |     def from_hf_config(
 122 |         cls,
 123 |         hf_config: PretrainedConfig,
 124 |         is_critic: bool = False,
 125 |         **kwargs,
 126 |     ) -> <Model>ModelArgs:
 127 |         # Map HF config fields to Archon model args
 128 |         ...
 129 | ```
 130 | 
 131 | ### Step 4: Implement `model.py`
 132 | 
 133 | Adapt the model architecture to match the target model.
 134 | 
 135 | **Key components to adapt**:
 136 | 
 137 | 1. **Normalization** (`RMSNorm` or similar):
 138 | 
 139 |    - Check if `elementwise_affine` is configurable
 140 |    - Check the epsilon default value
 141 |    - If the model uses `LayerNorm`, implement accordingly
 142 | 
 143 | 1. **Attention** module:
 144 | 
 145 |    - Q/K/V projection: Check bias presence (`nn.Linear(..., bias=True/False)`)
 146 |    - QK norm: Add `q_norm`/`k_norm` if the model has them, remove if it doesn't
 147 |    - GQA: `n_kv_heads` \< `n_heads` for grouped-query attention
 148 |    - Ulysses SP: Keep the `set_cp_group` / `_sp_enabled` pattern from the reference
 149 |    - Output projection: Check bias presence
 150 | 
 151 | 1. **FeedForward** module:
 152 | 
 153 |    - SwiGLU: `w2(silu(w1(x)) * w3(x))` -- most common for modern LLMs
 154 |    - Check bias in linear layers
 155 |    - For MoE models: `MoE` module replaces `FeedForward` on designated layers
 156 | 
 157 | 1. **TransformerBlock**: Pre-norm (most modern LLMs) vs post-norm
 158 | 
 159 |    - MoE layer detection via `_is_moe_layer()` if applicable
 160 | 
 161 | 1. **Top-level Model** (`<Model>Model(BaseArchonModel)`):
 162 | 
 163 |    - `tok_embeddings`, `layers` (as `ModuleDict`), `norm`, `output`/`score`
 164 |    - `init_weights()`: Match initialization scheme from HF
 165 |    - `init_buffers()`: RoPE cache + MoE buffers
 166 |    - `forward()`: Must follow `BaseArchonModel` signature:
 167 |      `(tokens, positions, cu_seqlens, max_seqlen, tree_attn_meta=None) -> Tensor`
 168 | 
 169 | **Base class contract** (`BaseArchonModel`):
 170 | 
 171 | ```python
 172 | class <Model>Model(BaseArchonModel):
 173 |     def forward(self, tokens, positions, cu_seqlens, max_seqlen, tree_attn_meta=None) -> torch.Tensor: ...
 174 |     def init_weights(self) -> None: ...
 175 |     def init_buffers(self, buffer_device) -> None: ...
 176 | ```
 177 | 
 178 | ### Step 5: Implement `rope.py`
 179 | 
 180 | Handle the rotary position embedding variant.
 181 | 
 182 | **Options**:
 183 | 
 184 | 1. **Standard RoPE** (same as qwen2/qwen3): Re-export from qwen2:
 185 | 
 186 |    ```python
 187 |    from areal.experimental.models.archon.qwen2.model.rope import (
 188 |        apply_rotary_emb,
 189 |        precompute_rope_cache,
 190 |        repeat_kv,
 191 |        reshape_for_broadcast,
 192 |        rotate_half,
 193 |    )
 194 |    ```
 195 | 
 196 | 1. **Custom RoPE** (YaRN, NTK-aware, etc.): Implement custom `precompute_rope_cache()`
 197 |    and `apply_rotary_emb()` functions. The key difference is usually in how `inv_freq`
 198 |    is computed (scaling factors, interpolation, etc.).
 199 | 
 200 | ### Step 6: Implement `state_dict_adapter.py`
 201 | 
 202 | Map between HuggingFace and Archon weight key names.
 203 | 
 204 | **This is the most error-prone step.** The adapter must correctly handle:
 205 | 
 206 | 1. **Key name mapping** (`from_hf_map` dict):
 207 | 
 208 |    - Embedding: `model.embed_tokens.weight` -> `tok_embeddings.weight`
 209 |    - Attention: `model.layers.{}.self_attn.q_proj.weight` ->
 210 |      `layers.{}.attention.wq.weight`
 211 |    - FFN: `model.layers.{}.mlp.gate_proj.weight` -> `layers.{}.feed_forward.w1.weight`
 212 |    - Norms: `model.layers.{}.input_layernorm.weight` ->
 213 |      `layers.{}.attention_norm.weight`
 214 |    - Output: `lm_head.weight` -> `output.weight`
 215 |    - Skip keys (set to `None`): `rotary_emb.inv_freq` (computed at runtime)
 216 |    - Model-specific keys: bias terms, QK norm weights, etc.
 217 | 
 218 | 1. **Reverse mapping** (`to_hf_map`): Auto-generated from `from_hf_map`
 219 | 
 220 | 1. **MoE expert weights** (if applicable): 3D\<->2D conversion for expert weights. Copy
 221 |    the MoE handling from qwen3 if the model has MoE.
 222 | 
 223 | 1. **Weight tying**: Skip `output.weight` during `to_hf()` if `tie_word_embeddings=True`
 224 | 
 225 | **Verification approach**: After implementation, the adapter should satisfy:
 226 | 
 227 | ```python
 228 | # Roundtrip: archon -> hf -> archon preserves all keys
 229 | hf_sd = adapter.to_hf(archon_sd)
 230 | roundtrip_sd = adapter.from_hf(hf_sd)
 231 | assert set(roundtrip_sd.keys()) == set(archon_sd.keys())
 232 | ```
 233 | 
 234 | **Base class contract** (`BaseStateDictAdapter`):
 235 | 
 236 | ```python
 237 | class <Model>StateDictAdapter(BaseStateDictAdapter):
 238 |     def from_hf(self, hf_state_dict) -> dict[str, Any]: ...
 239 |     def to_hf(self, archon_state_dict) -> dict[str, Any]: ...
 240 |     def convert_single_to_hf(self, name, tensor) -> list[tuple[str, torch.Tensor]]: ...
 241 | ```
 242 | 
 243 | ### Step 7: Implement `parallelize.py`
 244 | 
 245 | Define the parallelization strategy for the model.
 246 | 
 247 | **The parallelize function** applies parallelism in this order:
 248 | 
 249 | 1. TP (Tensor Parallelism) -- shard attention/FFN across devices
 250 | 1. EP (Expert Parallelism) -- for MoE models only
 251 | 1. CP (Context Parallelism / Ulysses SP) -- sequence parallelism
 252 | 1. AC (Activation Checkpointing) -- memory optimization
 253 | 1. torch.compile -- compilation optimization
 254 | 1. FSDP (Fully Sharded Data Parallelism) -- data parallelism
 255 | 
 256 | **Key adaptations by model architecture**:
 257 | 
 258 | - **Attention with QK norm**: wq/wk use `use_local_output=False` (DTensor output for
 259 |   norm), add `SequenceParallel(sequence_dim=2)` for q_norm/k_norm
 260 | - **Attention without QK norm**: wq/wk/wv all use `use_local_output=True`
 261 | - **Attention with bias**: Bias terms follow the same parallel plan as their weights
 262 | - **MoE layers**: Separate TP plan for MoE input/output, router gate, and expert
 263 |   weights. Copy from qwen3's `apply_moe_ep_tp()` and `apply_non_moe_tp()`
 264 | - **Dense-only models**: Simpler plan without MoE handling. Copy from qwen2
 265 | 
 266 | **Function signature** (must match `ParallelizeFn` protocol):
 267 | 
 268 | ```python
 269 | def parallelize_<model>(
 270 |     model: nn.Module,
 271 |     parallel_dims: ArchonParallelDims,
 272 |     param_dtype: torch.dtype = torch.bfloat16,
 273 |     reduce_dtype: torch.dtype = torch.float32,
 274 |     loss_parallel: bool = True,
 275 |     cpu_offload: bool = False,
 276 |     reshard_after_forward_policy: str = "default",
 277 |     ac_config: ActivationCheckpointConfig | None = None,
 278 |     enable_compile: bool = True,
 279 | ) -> nn.Module:
 280 | ```
 281 | 
 282 | ### Step 8: Create `spec.py` and Register
 283 | 
 284 | Assemble the `ModelSpec` and register it.
 285 | 
 286 | ```python
 287 | from areal.experimental.models.archon.model_spec import ModelSpec, register_model_spec
 288 | from areal.experimental.models.archon.pipeline_parallel import pipeline_llm
 289 | from areal.experimental.models.archon.<model>.infra.parallelize import parallelize_<model>
 290 | from areal.experimental.models.archon.<model>.model.args import <Model>ModelArgs
 291 | from areal.experimental.models.archon.<model>.model.model import <Model>Model
 292 | from areal.experimental.models.archon.<model>.model.state_dict_adapter import (
 293 |     <Model>StateDictAdapter,
 294 | )
 295 | 
 296 | <MODEL>_SPEC = ModelSpec(
 297 |     name="<Model>",
 298 |     model_class=<Model>Model,
 299 |     model_args_class=<Model>ModelArgs,
 300 |     state_dict_adapter_class=<Model>StateDictAdapter,
 301 |     parallelize_fn=parallelize_<model>,
 302 |     supported_model_types=frozenset({"<model_type>"}),  # From HF config.json
 303 |     pipelining_fn=pipeline_llm,
 304 | )
 305 | 
 306 | # Auto-register when module is imported
 307 | register_model_spec(<MODEL>_SPEC)
 308 | 
 309 | __all__ = ["<MODEL>_SPEC"]
 310 | ```
 311 | 
 312 | **Note**: `supported_model_types` should include all HF `model_type` strings that this
 313 | implementation handles (e.g., `{"qwen3", "qwen3_moe"}` for Qwen3).
 314 | 
 315 | ### Step 9: Register in `__init__.py`
 316 | 
 317 | Add the import to `areal/experimental/models/archon/__init__.py`:
 318 | 
 319 | ```python
 320 | from areal.experimental.models.archon.<model> import spec as <model>_spec  # noqa: F401
 321 | ```
 322 | 
 323 | This triggers auto-registration when the module is imported.
 324 | 
 325 | ### Step 10: Verify and Test
 326 | 
 327 | Verification should be done in stages, adapting based on available hardware and the test
 328 | patterns in `tests/experimental/archon/`.
 329 | 
 330 | **Before writing tests**, examine the existing test files to understand current
 331 | patterns:
 332 | 
 333 | ```
 334 | tests/experimental/archon/
 335 |   conftest.py             -- Pytest configuration (version checks)
 336 |   utils.py                -- Shared utilities (model loading, comparison)
 337 |   test_qwen3_args.py      -- Args unit tests (CPU-only)
 338 |   test_state_dict_adapter.py  -- State dict roundtrip tests
 339 |   test_weight_sync.py     -- Weight completeness tests (meta device)
 340 |   test_forward.py         -- Forward precision comparison (single GPU)
 341 |   ...
 342 | ```
 343 | 
 344 | **Test stages** (write tests appropriate for the model's complexity):
 345 | 
 346 | #### Stage 1: Args Tests (CPU-only, always write these)
 347 | 
 348 | Test `from_hf_config()` with mock HuggingFace configs:
 349 | 
 350 | ```python
 351 | # Pattern: Create mock PretrainedConfig, verify args mapping
 352 | from unittest.mock import MagicMock
 353 | 
 354 | def test_args_from_hf_config():
 355 |     hf_config = MagicMock()
 356 |     hf_config.hidden_size = 4096
 357 |     hf_config.num_hidden_layers = 32
 358 |     # ... set all required fields
 359 |     args = <Model>ModelArgs.from_hf_config(hf_config)
 360 |     assert args.dim == 4096
 361 |     assert args.n_layers == 32
 362 | ```
 363 | 
 364 | #### Stage 2: State Dict Adapter Tests (CPU-only)
 365 | 
 366 | Test key mapping roundtrip:
 367 | 
 368 | ```python
 369 | def test_state_dict_roundtrip():
 370 |     # Create adapter with mock config
 371 |     adapter = <Model>StateDictAdapter(mock_config)
 372 |     # Create fake archon state dict with expected keys
 373 |     archon_sd = {"tok_embeddings.weight": torch.randn(vocab, dim), ...}
 374 |     # Roundtrip
 375 |     hf_sd = adapter.to_hf(archon_sd)
 376 |     roundtrip = adapter.from_hf(hf_sd)
 377 |     assert set(roundtrip.keys()) == set(archon_sd.keys())
 378 | ```
 379 | 
 380 | #### Stage 3: Weight Completeness (meta device, CPU-only)
 381 | 
 382 | Verify all model parameters have HF mappings:
 383 | 
 384 | ```python
 385 | def test_weight_completeness():
 386 |     # Create model on meta device
 387 |     with torch.device("meta"):
 388 |         model = <Model>Model(args)
 389 |     adapter = <Model>StateDictAdapter(hf_config)
 390 |     # Check every archon param has a HF mapping
 391 |     for name, _ in model.named_parameters():
 392 |         hf_pairs = adapter.convert_single_to_hf(name, torch.empty(0))
 393 |         assert len(hf_pairs) > 0, f"No HF mapping for {name}"
 394 | ```
 395 | 
 396 | #### Stage 4: Forward Precision (single GPU, if available)
 397 | 
 398 | Compare Archon model output against HuggingFace reference:
 399 | 
 400 | ```python
 401 | @pytest.mark.skipif(not torch.cuda.is_available(), reason="Requires CUDA")
 402 | def test_forward_matches_hf():
 403 |     # Load both HF and Archon models
 404 |     # Run forward on same input
 405 |     # Compare logits within tolerance
 406 | ```
 407 | 
 408 | **Important**: Do NOT hardcode the test categories. Inspect the existing test files in
 409 | `tests/experimental/archon/` and follow the same patterns, fixtures, and markers. Adapt
 410 | test scope to the model's specific features (e.g., add MoE-specific tests only if the
 411 | model has MoE).
 412 | 
 413 | ## Reference Implementations
 414 | 
 415 | | Model | Directory                                 | Features                                                |
 416 | | ----- | ----------------------------------------- | ------------------------------------------------------- |
 417 | | Qwen2 | `areal/experimental/models/archon/qwen2/` | Dense, attention bias, no QK norm                       |
 418 | | Qwen3 | `areal/experimental/models/archon/qwen3/` | Dense + MoE, QK norm, no attention bias, shared experts |
 419 | 
 420 | ## Architecture Decision Map
 421 | 
 422 | | Feature             | qwen2    | qwen3                      | What to check in target model                            |
 423 | | ------------------- | -------- | -------------------------- | -------------------------------------------------------- |
 424 | | Attention bias      | Yes      | No                         | `attention_bias` in HF config                            |
 425 | | QK norm             | No       | Yes                        | `qk_norm` in HF config or QKNorm module in modeling file |
 426 | | MoE                 | No       | Yes                        | `num_experts`/`num_local_experts` in HF config           |
 427 | | Shared experts      | No       | Yes                        | `num_shared_experts` in HF config                        |
 428 | | Decoder sparse step | No       | Yes                        | `decoder_sparse_step` in HF config                       |
 429 | | Weight tying        | Both     | Both                       | `tie_word_embeddings` in HF config                       |
 430 | | RoPE                | Standard | Standard (re-export qwen2) | Check inv_freq formula in HF modeling code               |
 431 | 
 432 | ## Common Mistakes
 433 | 
 434 | - Not mapping all HF keys in `state_dict_adapter.py` (causes silent weight drops)
 435 | - Wrong `from_hf_config()` field mapping (uses wrong HF config attribute name)
 436 | - Forgetting to handle `None` keys in `from_hf_map` (keys to skip like
 437 |   `rotary_emb.inv_freq`)
 438 | - Missing MoE expert weight 3D\<->2D conversion when model has MoE
 439 | - Wrong TP plan for attention with/without QK norm (`use_local_output` must match)
 440 | - Forgetting to add import line in `areal/experimental/models/archon/__init__.py`
 441 | - Not including all `model_type` variants in `supported_model_types` frozenset
 442 | - Using `print` instead of `areal.utils.logging.getLogger()`
 443 | 
 444 | ## File Checklist
 445 | 
 446 | After completion, verify all files exist and are consistent:
 447 | 
 448 | - [ ] `areal/experimental/models/archon/<model>/__init__.py`
 449 | - [ ] `areal/experimental/models/archon/<model>/spec.py` -- ModelSpec + register
 450 | - [ ] `areal/experimental/models/archon/<model>/model/args.py` -- ModelArgs +
 451 |   from_hf_config
 452 | - [ ] `areal/experimental/models/archon/<model>/model/model.py` -- Model + Attention +
 453 |   FFN
 454 | - [ ] `areal/experimental/models/archon/<model>/model/rope.py` -- RoPE (or re-export)
 455 | - [ ] `areal/experimental/models/archon/<model>/model/state_dict_adapter.py` -- Key
 456 |   mapping
 457 | - [ ] `areal/experimental/models/archon/<model>/infra/parallelize.py` -- Parallel
 458 |   strategy
 459 | - [ ] `areal/experimental/models/archon/__init__.py` -- Import line added
 460 | - [ ] `tests/experimental/archon/test_<model>_*.py` -- Tests
 461 | 
 462 | ______________________________________________________________________
 463 | 
 464 | <!--
 465 | ================================================================================
 466 |                             MAINTAINER GUIDE
 467 | ================================================================================
 468 | 
 469 | Location: .opencode/skills/add-archon-model/SKILL.md
 470 | Invocation: /add-archon-model <model_name>
 471 | 
 472 | ## Purpose
 473 | 
 474 | Semi-automated guide for adding new model architectures to the Archon training engine.
 475 | Unlike simpler skills (add-reward, add-dataset), this skill actively guides Claude to:
 476 | 1. Analyze HuggingFace source code to extract architecture details
 477 | 2. Select the closest reference implementation (qwen2 or qwen3)
 478 | 3. Generate code skeletons adapted to the target architecture
 479 | 4. Create appropriate tests based on existing test patterns
 480 | 
 481 | ## How to Update
 482 | 
 483 | ### When New Reference Models Are Added
 484 | 1. Add to "Reference Implementations" table
 485 | 2. Update "Architecture Decision Map" with new feature columns
 486 | 3. Update Step 2 (reference selection) with new options
 487 | 
 488 | ### When Base Classes Change
 489 | 1. Update contract signatures in Steps 3, 4, 6, 7
 490 | 2. Update file checklist if new files are required
 491 | 
 492 | ### When ModelSpec Changes
 493 | 1. Update Step 8 with new ModelSpec fields
 494 | 2. Update spec.py template
 495 | 
 496 | ### When Test Patterns Change
 497 | 1. Update Step 10 with new test patterns
 498 | 2. Do NOT hardcode test categories -- keep it flexible
 499 | 
 500 | ### Important Design Decisions
 501 | - This skill is SEMI-AUTOMATED: Claude should read HF source and generate code,
 502 |   not just provide templates for the user to fill in manually
 503 | - The skill references existing test files rather than hardcoding test categories,
 504 |   ensuring it stays current as the test suite evolves
 505 | - Reference model selection (qwen2 vs qwen3) is based on MoE and QK norm presence
 506 | 
 507 | ================================================================================
 508 | -->
```


---
## .opencode/skills/add-dataset/SKILL.md

```
   1 | ---
   2 | name: add-dataset
   3 | description: Guide for adding a new dataset loader to AReaL. Use when user wants to add a new dataset.
   4 | ---
   5 | 
   6 | # Add Dataset
   7 | 
   8 | Add a new dataset loader to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a dataset?"
  15 | - User wants to integrate a new dataset
  16 | - User mentions creating a dataset loader
  17 | 
  18 | ## Step-by-Step Guide
  19 | 
  20 | ### Step 1: Create Dataset File
  21 | 
  22 | Create `areal/dataset/<name>.py`:
  23 | 
  24 | ```python
  25 | from datasets import Dataset, load_dataset
  26 | 
  27 | 
  28 | def get_<name>_sft_dataset(
  29 |     path: str,
  30 |     split: str,
  31 |     tokenizer,
  32 |     max_length: int | None = None,
  33 | ) -> Dataset:
  34 |     """Load dataset for SFT training.
  35 | 
  36 |     Args:
  37 |         path: Path to dataset (HuggingFace hub or local path)
  38 |         split: Dataset split (train/validation/test)
  39 |         tokenizer: Tokenizer for processing
  40 |         max_length: Maximum sequence length (optional)
  41 | 
  42 |     Returns:
  43 |         HuggingFace Dataset with processed samples
  44 |     """
  45 |     dataset = load_dataset(path=path, split=split)
  46 | 
  47 |     def process(sample):
  48 |         # Tokenize the full sequence (prompt + response)
  49 |         seq_token = tokenizer.encode(
  50 |             sample["question"] + sample["answer"] + tokenizer.eos_token
  51 |         )
  52 |         prompt_token = tokenizer.encode(sample["question"])
  53 |         # Loss mask: 0 for prompt, 1 for response
  54 |         loss_mask = [0] * len(prompt_token) + [1] * (len(seq_token) - len(prompt_token))
  55 |         return {"input_ids": seq_token, "loss_mask": loss_mask}
  56 | 
  57 |     dataset = dataset.map(process).remove_columns(["question", "answer"])
  58 | 
  59 |     if max_length is not None:
  60 |         dataset = dataset.filter(lambda x: len(x["input_ids"]) <= max_length)
  61 | 
  62 |     return dataset
  63 | 
  64 | 
  65 | def get_<name>_rl_dataset(
  66 |     path: str,
  67 |     split: str,
  68 |     tokenizer,
  69 |     max_length: int | None = None,
  70 | ) -> Dataset:
  71 |     """Load dataset for RL training.
  72 | 
  73 |     Args:
  74 |         path: Path to dataset
  75 |         split: Dataset split
  76 |         tokenizer: Tokenizer for length filtering
  77 |         max_length: Maximum sequence length
  78 | 
  79 |     Returns:
  80 |         HuggingFace Dataset with prompts and answers for reward computation
  81 |     """
  82 |     dataset = load_dataset(path=path, split=split)
  83 | 
  84 |     def process(sample):
  85 |         messages = [
  86 |             {
  87 |                 "role": "user",
  88 |                 "content": sample["question"],
  89 |             }
  90 |         ]
  91 |         return {"messages": messages, "answer": sample["answer"]}
  92 | 
  93 |     dataset = dataset.map(process).remove_columns(["question"])
  94 | 
  95 |     if max_length is not None:
  96 | 
  97 |         def filter_length(sample):
  98 |             content = sample["messages"][0]["content"]
  99 |             tokens = tokenizer.encode(content)
 100 |             return len(tokens) <= max_length
 101 | 
 102 |         dataset = dataset.filter(filter_length)
 103 | 
 104 |     return dataset
 105 | ```
 106 | 
 107 | ### Step 2: Register in __init__.py
 108 | 
 109 | Update `areal/dataset/__init__.py`:
 110 | 
 111 | ```python
 112 | # Add to VALID_DATASETS
 113 | VALID_DATASETS = [
 114 |     # ... existing datasets
 115 |     "<name>",
 116 | ]
 117 | 
 118 | # Add to _get_custom_dataset function
 119 | def _get_custom_dataset(name: str, ...):
 120 |     # ... existing code
 121 |     elif name == "<name>":
 122 |         from areal.dataset.<name> import get_<name>_sft_dataset, get_<name>_rl_dataset
 123 |         if dataset_type == "sft":
 124 |             return get_<name>_sft_dataset(path, split, max_length, tokenizer)
 125 |         else:
 126 |             return get_<name>_rl_dataset(path, split, max_length, tokenizer)
 127 | ```
 128 | 
 129 | ### Step 3: Add Config (Optional)
 130 | 
 131 | If the dataset needs special configuration, add to `areal/api/cli_args.py`:
 132 | 
 133 | ```python
 134 | @dataclass
 135 | class TrainDatasetConfig:
 136 |     # ... existing fields
 137 |     <name>_specific_field: Optional[str] = None
 138 | ```
 139 | 
 140 | ### Step 4: Add Tests
 141 | 
 142 | Create `tests/test_<name>_dataset.py`:
 143 | 
 144 | ```python
 145 | import pytest
 146 | from areal.dataset.<name> import get_<name>_sft_dataset, get_<name>_rl_dataset
 147 | 
 148 | def test_sft_dataset_loads(tokenizer):
 149 |     dataset = get_<name>_sft_dataset("path/to/data", split="train", tokenizer=tokenizer)
 150 |     assert len(dataset) > 0
 151 |     assert "input_ids" in dataset.column_names
 152 |     assert "loss_mask" in dataset.column_names
 153 | 
 154 | def test_rl_dataset_loads(tokenizer):
 155 |     dataset = get_<name>_rl_dataset("path/to/data", split="train", tokenizer=tokenizer)
 156 |     assert len(dataset) > 0
 157 |     assert "messages" in dataset.column_names
 158 |     assert "answer" in dataset.column_names
 159 | ```
 160 | 
 161 | ## Reference Implementations
 162 | 
 163 | | Dataset    | File                               | Description              |
 164 | | ---------- | ---------------------------------- | ------------------------ |
 165 | | GSM8K      | `areal/dataset/gsm8k.py`           | Math word problems       |
 166 | | Geometry3K | `areal/dataset/geometry3k.py`      | Geometry problems        |
 167 | | CLEVR      | `areal/dataset/clevr_count_70k.py` | Visual counting          |
 168 | | HH-RLHF    | `areal/dataset/hhrlhf.py`          | Helpfulness/Harmlessness |
 169 | | TORL       | `areal/dataset/torl_data.py`       | Tool-use RL              |
 170 | 
 171 | ## Required Fields
 172 | 
 173 | ### SFT Dataset
 174 | 
 175 | ```python
 176 | {
 177 |     "messages": [
 178 |         {"role": "user", "content": "..."},
 179 |         {"role": "assistant", "content": "..."},
 180 |     ]
 181 | }
 182 | ```
 183 | 
 184 | ### RL Dataset
 185 | 
 186 | ```python
 187 | {
 188 |     "messages": [
 189 |         {"role": "user", "content": "..."},
 190 |     ],
 191 |     "answer": "ground_truth_for_reward",
 192 |     # Optional metadata for reward function
 193 | }
 194 | ```
 195 | 
 196 | ## Common Mistakes
 197 | 
 198 | - Returning `List[Dict]` instead of HuggingFace `Dataset`
 199 | - Using Python loops instead of `dataset.map()`/`filter()`
 200 | - Missing `"messages"` field for RL datasets
 201 | - Wrong message format (should be list of dicts with `role` and `content`)
 202 | - Not registering in `__init__.py`
 203 | 
 204 | ______________________________________________________________________
 205 | 
 206 | <!--
 207 | ================================================================================
 208 |                             MAINTAINER GUIDE
 209 | ================================================================================
 210 | 
 211 | Location: .opencode/skills/add-dataset/SKILL.md
 212 | Invocation: /add-dataset <name>
 213 | 
 214 | ## Purpose
 215 | 
 216 | Step-by-step guide for adding new dataset loaders.
 217 | 
 218 | ## How to Update
 219 | 
 220 | ### When Dataset API Changes
 221 | 1. Update the code templates
 222 | 2. Update required fields section
 223 | 3. Update registration example
 224 | 
 225 | ### When New Dataset Types Added
 226 | 1. Add to "Reference Implementations" table
 227 | 2. Add any new required fields
 228 | 
 229 | ================================================================================
 230 | -->
```


---
## .opencode/skills/add-reward/SKILL.md

```
   1 | ---
   2 | name: add-reward
   3 | description: Guide for adding a new reward function to AReaL. Use when user wants to create a reward function.
   4 | ---
   5 | 
   6 | # Add Reward
   7 | 
   8 | Add a new reward function to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a reward function?"
  15 | - User wants to implement custom rewards
  16 | - User mentions reward computation
  17 | 
  18 | ## Step-by-Step Guide
  19 | 
  20 | ### Step 1: Create Reward File
  21 | 
  22 | Create `areal/reward/<name>.py`:
  23 | 
  24 | ```python
  25 | from typing import Any
  26 | 
  27 | from areal.utils import logging
  28 | 
  29 | logger = logging.getLogger("MyReward")
  30 | 
  31 | 
  32 | def <name>_reward_fn(
  33 |     prompt: str,
  34 |     completions: str,
  35 |     prompt_ids,
  36 |     completion_ids,
  37 |     answer: str | None = None,
  38 |     **kwargs: Any,
  39 | ) -> float:
  40 |     """Compute reward for a single completion.
  41 | 
  42 |     Args:
  43 |         prompt: Prompt string
  44 |         completions: Completion string (model output)
  45 |         prompt_ids: Tokenized prompt IDs
  46 |         completion_ids: Tokenized completion IDs
  47 |         answer: Ground truth answer from dataset (optional)
  48 |         **kwargs: Additional data from dataset
  49 | 
  50 |     Returns:
  51 |         Reward value (float), typically 0.0 or 1.0
  52 |     """
  53 |     try:
  54 |         # Extract answer from completion
  55 |         extracted = _extract_answer(completions)
  56 | 
  57 |         # Compare with ground truth
  58 |         if answer is not None and extracted == str(answer):
  59 |             return 1.0
  60 |         return 0.0
  61 |     except Exception:
  62 |         logger.warning("Exception in reward computation", exc_info=True)
  63 |         return 0.0
  64 | 
  65 | 
  66 | def _extract_answer(completion: str) -> str:
  67 |     """Extract the answer from a completion string.
  68 | 
  69 |     Implement your extraction logic here.
  70 |     """
  71 |     # Example: Extract content from \boxed{}
  72 |     import re
  73 | 
  74 |     match = re.search(r"\\boxed\{([^}]+)\}", completion)
  75 |     if match:
  76 |         return match.group(1).strip()
  77 |     return completion.strip()
  78 | ```
  79 | 
  80 | ### Step 2: Register in __init__.py
  81 | 
  82 | Update `areal/reward/__init__.py`:
  83 | 
  84 | ```python
  85 | # Add to VALID_REWARD_FN
  86 | VALID_REWARD_FN = [
  87 |     # ... existing reward functions
  88 |     "<name>",
  89 | ]
  90 | 
  91 | # Add to get_reward_fn function
  92 | def get_reward_fn(name: str, **kwargs):
  93 |     # ... existing code
  94 |     elif name == "<name>":
  95 |         from areal.reward.<name> import <name>_reward_fn
  96 |         return <name>_reward_fn
  97 | ```
  98 | 
  99 | ### Step 3: Handle Blocking Operations
 100 | 
 101 | If your reward function uses blocking operations (e.g., API calls, model inference), the
 102 | workflow will wrap it with `AsyncRewardWrapper`:
 103 | 
 104 | ```python
 105 | # In your workflow
 106 | from areal.reward import AsyncRewardWrapper
 107 | 
 108 | self.reward_fn = AsyncRewardWrapper(reward_fn)
 109 | 
 110 | # Then call it asynchronously
 111 | rewards = await self.reward_fn(prompt, completions, **data)
 112 | ```
 113 | 
 114 | ### Step 4: Add Tests
 115 | 
 116 | Create `tests/test_<name>_reward.py`:
 117 | 
 118 | ```python
 119 | import pytest
 120 | from areal.reward.<name> import <name>_reward_fn
 121 | 
 122 | def test_reward_correct_answer():
 123 |     reward = <name>_reward_fn(
 124 |         prompt="What is 2+2?",
 125 |         completions="The answer is \\boxed{4}",
 126 |         prompt_ids=None,
 127 |         completion_ids=None,
 128 |         answer="4",
 129 |     )
 130 |     assert reward == 1.0
 131 | 
 132 | def test_reward_wrong_answer():
 133 |     reward = <name>_reward_fn(
 134 |         prompt="What is 2+2?",
 135 |         completions="The answer is \\boxed{5}",
 136 |         prompt_ids=None,
 137 |         completion_ids=None,
 138 |         answer="4",
 139 |     )
 140 |     assert reward == 0.0
 141 | ```
 142 | 
 143 | ## Reference Implementations
 144 | 
 145 | | Reward     | File                              | Description                  |
 146 | | ---------- | --------------------------------- | ---------------------------- |
 147 | | GSM8K      | `areal/reward/gsm8k.py`           | Math answer verification     |
 148 | | Geometry3K | `areal/reward/geometry3k.py`      | Geometry answer verification |
 149 | | CLEVR      | `areal/reward/clevr_count_70k.py` | Counting verification        |
 150 | | MathVerify | `areal/reward/math_verify.py`     | General math verification    |
 151 | 
 152 | ## Function Signature
 153 | 
 154 | All reward functions must follow this signature:
 155 | 
 156 | ```python
 157 | def reward_fn(
 158 |     prompt: str,               # Input prompt string
 159 |     completions: str,          # Model completion string
 160 |     prompt_ids,                # Tokenized prompt
 161 |     completion_ids,            # Tokenized completion
 162 |     **kwargs: Any,             # Additional data from dataset (e.g., answer)
 163 | ) -> float:                    # Reward value (typically 0.0 or 1.0)
 164 | ```
 165 | 
 166 | **Note**: The reward function is called once per sample. Batching is handled by
 167 | `AsyncRewardWrapper` in the workflow.
 168 | 
 169 | ## Key Requirements
 170 | 
 171 | 1. **Deterministic**: Same inputs should produce same outputs
 172 | 1. **Return float**: Output is a single float value per sample
 173 | 1. **No blocking in async context**: Use `AsyncRewardWrapper` if needed
 174 | 1. **Logging**: Use `areal.utils.logging`, not `print`
 175 | 1. **Handle exceptions**: Return 0.0 on error, don't raise
 176 | 
 177 | ## Common Mistakes
 178 | 
 179 | - Returning a tensor instead of a float
 180 | - Expecting batched inputs (reward is called per sample)
 181 | - Non-deterministic behavior
 182 | - Blocking operations without `AsyncRewardWrapper`
 183 | - Raising exceptions instead of returning 0.0
 184 | 
 185 | ______________________________________________________________________
 186 | 
 187 | <!--
 188 | ================================================================================
 189 |                             MAINTAINER GUIDE
 190 | ================================================================================
 191 | 
 192 | Location: .opencode/skills/add-reward/SKILL.md
 193 | Invocation: /add-reward <name>
 194 | 
 195 | ## Purpose
 196 | 
 197 | Step-by-step guide for adding new reward functions.
 198 | 
 199 | ## How to Update
 200 | 
 201 | ### When Reward API Changes
 202 | 1. Update the function signature section
 203 | 2. Update the code template
 204 | 3. Update key requirements
 205 | 
 206 | ### When New Reward Patterns Emerge
 207 | 1. Add to "Reference Implementations" table
 208 | 2. Add examples for new patterns
 209 | 
 210 | ================================================================================
 211 | -->
```


---
## .opencode/skills/add-unit-tests/SKILL.md

```
   1 | ---
   2 | name: add-unit-tests
   3 | description: Guide for adding unit tests to AReaL. Use when user wants to add tests for new functionality or increase test coverage.
   4 | ---
   5 | 
   6 | # Add Unit Tests
   7 | 
   8 | Add unit tests to AReaL following the project's testing conventions.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add tests?"
  15 | - User wants to increase test coverage
  16 | - User needs to write tests for new functionality
  17 | - User wants to understand AReaL testing patterns
  18 | 
  19 | ## Step-by-Step Guide
  20 | 
  21 | ### Step 1: Understand Test Types
  22 | 
  23 | AReaL has two main test categories:
  24 | 
  25 | | Test Type             | Purpose                            | Location Pattern                   | How It Runs                                |
  26 | | --------------------- | ---------------------------------- | ---------------------------------- | ------------------------------------------ |
  27 | | **Unit Tests**        | Test individual functions/modules  | `tests/test_<module>_<feature>.py` | Directly via pytest                        |
  28 | | **Distributed Tests** | Test distributed/parallel behavior | `tests/torchrun/run_*.py`          | Via torchrun (called by pytest subprocess) |
  29 | 
  30 | **Note**: All tests are invoked via pytest. Distributed tests use `torchrun` but are
  31 | still called from pytest test files.
  32 | 
  33 | ### Step 2: Create Test File Structure
  34 | 
  35 | Create test file with naming convention: `test_<module>_<feature>.py`
  36 | 
  37 | ```python
  38 | import pytest
  39 | import torch
  40 | 
  41 | # Import the module to test
  42 | from areal.dataset.gsm8k import get_gsm8k_sft_dataset
  43 | from tests.utils import get_dataset_path  # Optional test utilities
  44 | # For mocking tokenizer: from unittest.mock import MagicMock
  45 | ```
  46 | 
  47 | ### Step 3: Write Test Functions
  48 | 
  49 | Follow Arrange-Act-Assert pattern:
  50 | 
  51 | ```python
  52 | def test_function_under_condition_returns_expected():
  53 |     """Test that function returns expected value under condition."""
  54 |     # Arrange
  55 |     input_data = 5
  56 |     expected_output = 10
  57 | 
  58 |     # Act
  59 |     result = function_under_test(input_data)
  60 | 
  61 |     # Assert
  62 |     assert result == expected_output
  63 | ```
  64 | 
  65 | ### Step 4: Add Pytest Markers and CI Strategy
  66 | 
  67 | Use appropriate pytest markers:
  68 | 
  69 | | Marker                                  | When to Use                                                  |
  70 | | --------------------------------------- | ------------------------------------------------------------ |
  71 | | `@pytest.mark.slow`                     | Test takes > 10 seconds (excluded from CI by default)        |
  72 | | `@pytest.mark.ci`                       | Slow test that must run in CI (use with `@pytest.mark.slow`) |
  73 | | `@pytest.mark.asyncio`                  | Async test functions                                         |
  74 | | `@pytest.mark.skipif(cond, reason=...)` | Conditional skip                                             |
  75 | | `@pytest.mark.parametrize(...)`         | Parameterized tests                                          |
  76 | 
  77 | **CI Test Strategy**:
  78 | 
  79 | - `@pytest.mark.slow`: Excluded from CI by default (CI runs `pytest -m "not slow"`)
  80 | - `@pytest.mark.slow` + `@pytest.mark.ci`: Slow but must run in CI
  81 | - No marker: Runs in CI (fast unit tests)
  82 | 
  83 | ```python
  84 | @pytest.mark.asyncio
  85 | async def test_async_function():
  86 |     result = await async_function()
  87 |     assert result == expected
  88 | 
  89 | @pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA not available")
  90 | def test_gpu_feature():
  91 |     tensor = torch.tensor([1, 2, 3], device="cuda")
  92 |     # ... assertions
  93 | 
  94 | @pytest.mark.parametrize("batch_size", [1, 4, 16])
  95 | def test_with_parameters(batch_size):
  96 |     # Parameterized test
  97 | 
  98 | @pytest.mark.slow
  99 | def test_slow_function():
 100 |     # Excluded from CI by default
 101 | 
 102 | @pytest.mark.slow
 103 | @pytest.mark.ci
 104 | def test_slow_but_required_in_ci():
 105 |     # Slow but must run in CI
 106 | ```
 107 | 
 108 | ### Step 5: Mock Distributed Environment
 109 | 
 110 | For unit tests that need distributed mocks:
 111 | 
 112 | ```python
 113 | import torch.distributed as dist
 114 | 
 115 | def test_distributed_function(monkeypatch):
 116 |     monkeypatch.setattr(dist, "get_rank", lambda: 0)
 117 |     monkeypatch.setattr(dist, "get_world_size", lambda: 2)
 118 |     result = distributed_function()
 119 |     assert result == expected
 120 | ```
 121 | 
 122 | ### Step 6: Handle GPU Dependencies
 123 | 
 124 | Always skip gracefully when GPU unavailable:
 125 | 
 126 | ```python
 127 | CUDA_AVAILABLE = torch.cuda.is_available()
 128 | 
 129 | @pytest.mark.skipif(not CUDA_AVAILABLE, reason="CUDA not available")
 130 | def test_gpu_function():
 131 |     tensor = torch.tensor([1, 2, 3], device="cuda")
 132 |     # ... assertions
 133 | ```
 134 | 
 135 | ## Key Requirements (Based on testing.md)
 136 | 
 137 | ### Mocking Distributed
 138 | 
 139 | - Use `torch.distributed.fake_pg` for unit tests
 140 | - Mock `dist.get_rank()` and `dist.get_world_size()` explicitly
 141 | - Don't mock internals of FSDP/DTensor
 142 | 
 143 | ### GPU Test Constraints
 144 | 
 145 | - **Always skip gracefully** when GPU unavailable
 146 | - Clean up GPU memory: `torch.cuda.empty_cache()` in fixtures
 147 | - Use smallest possible model/batch for unit tests
 148 | 
 149 | ### Assertions
 150 | 
 151 | - Use `torch.testing.assert_close()` for tensor comparison
 152 | - Specify `rtol`/`atol` explicitly for numerical tests
 153 | - Avoid bare `assert tensor.equal()` - no useful error message
 154 | 
 155 | ## Reference Implementations
 156 | 
 157 | | Test File                        | Description                            | Key Patterns                                      |
 158 | | -------------------------------- | -------------------------------------- | ------------------------------------------------- |
 159 | | `tests/test_utils.py`            | Utility function tests                 | Fixtures, parametrized tests                      |
 160 | | `tests/test_examples.py`         | Integration tests with dataset loading | Dataset path resolution, success pattern matching |
 161 | | `tests/test_fsdp_engine_nccl.py` | Distributed tests                      | Torchrun integration                              |
 162 | 
 163 | ## Common Mistakes
 164 | 
 165 | - **Missing test file registration**: Ensure file follows `test_*.py` naming
 166 | - **GPU dependency without skip**: Always use `@pytest.mark.skipif` for GPU tests
 167 | - **Incorrect tensor comparisons**: Use `torch.testing.assert_close()` not
 168 |   `assert tensor.equal()`
 169 | - **Memory leaks in GPU tests**: Clean up with `torch.cuda.empty_cache()`
 170 | - **Mocking too much**: Don't mock FSDP/DTensor internals
 171 | - **Unclear test names**: Follow `test_<what>_<condition>_<expected>` pattern
 172 | - **No docstrings**: Add descriptive docstrings to test functions
 173 | 
 174 | ## Integration with Other Skills
 175 | 
 176 | This skill complements other AReaL development skills:
 177 | 
 178 | - **After `/add-dataset`**: Add tests for new dataset loaders
 179 | - **After `/add-workflow`**: Add tests for new workflows
 180 | - **After `/add-reward`**: Add tests for new reward functions
 181 | - **With expert agents**: Reference this skill when planning test implementation
 182 | 
 183 | ## Running Tests
 184 | 
 185 | ```bash
 186 | # First check GPU availability (many tests require GPU)
 187 | python -c "import torch; print('GPU available:', torch.cuda.is_available())"
 188 | 
 189 | # Run specific test file
 190 | uv run pytest tests/test_<name>.py
 191 | 
 192 | # Skip slow tests (CI default)
 193 | uv run pytest -m "not slow"
 194 | 
 195 | # Run with verbose output
 196 | uv run pytest -v
 197 | 
 198 | # Run distributed tests (requires torchrun and multi-GPU)
 199 | # Note: Usually invoked via pytest test files
 200 | torchrun --nproc_per_node=2 tests/torchrun/run_<test>.py
 201 | ```
 202 | 
 203 | <!--
 204 | ================================================================================
 205 |                             MAINTAINER GUIDE
 206 | ================================================================================
 207 | 
 208 | Location: .opencode/skills/add-unit-tests/SKILL.md
 209 | Invocation: /add-unit-tests
 210 | 
 211 | ## Purpose
 212 | 
 213 | Step-by-step guide for adding unit tests to AReaL.
 214 | 
 215 | ## How to Update
 216 | 
 217 | ### When Testing Conventions Change
 218 | 1. Update "Key Requirements" section based on `testing.md`
 219 | 2. Update test examples to match new patterns
 220 | 3. Update reference implementations
 221 | 
 222 | ### When Test Types Need Update
 223 | 1. Update "Understand Test Types" table (currently two main types)
 224 | 2. Add new examples if needed
 225 | 3. Update common mistakes
 226 | 
 227 | ### Integration with Other Skills
 228 | Ensure references to other skills (`/add-dataset`, `/add-workflow`, `/add-reward`) remain accurate.
 229 | 
 230 | ================================================================================
 231 | -->
```


---
## .opencode/skills/add-workflow/SKILL.md

```
   1 | ---
   2 | name: add-workflow
   3 | description: Guide for adding a new RolloutWorkflow to AReaL. Use when user wants to create a new workflow.
   4 | ---
   5 | 
   6 | # Add Workflow
   7 | 
   8 | Add a new RolloutWorkflow implementation to AReaL.
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - User asks "how do I add a workflow?"
  15 | - User wants to create a new RolloutWorkflow
  16 | - User mentions implementing a custom rollout
  17 | 
  18 | ## Prerequisites
  19 | 
  20 | Before starting, ensure you understand:
  21 | 
  22 | - The workflow's purpose and requirements
  23 | - Input/output data format
  24 | - Reward function to use
  25 | 
  26 | ## Step-by-Step Guide
  27 | 
  28 | ### Step 1: Create Workflow File
  29 | 
  30 | Create `areal/workflow/<name>.py`:
  31 | 
  32 | ```python
  33 | import uuid
  34 | from typing import Any, Callable
  35 | 
  36 | import torch
  37 | 
  38 | from areal.api.cli_args import GenerationHyperparameters
  39 | from areal.api.engine_api import InferenceEngine
  40 | from areal.api.io_struct import ModelRequest, ModelResponse
  41 | from areal.api.reward_api import AsyncRewardWrapper
  42 | from areal.api.workflow_api import RolloutWorkflow
  43 | from areal.utils import logging
  44 | 
  45 | logger = logging.getLogger("MyWorkflow")
  46 | 
  47 | 
  48 | class MyWorkflow(RolloutWorkflow):
  49 |     """Description of your workflow."""
  50 | 
  51 |     def __init__(
  52 |         self,
  53 |         gconfig: GenerationHyperparameters,
  54 |         tokenizer,
  55 |         reward_fn: Callable,
  56 |     ):
  57 |         self.gconfig = gconfig.new_with_stop_and_pad_token_ids(tokenizer)
  58 |         self.tokenizer = tokenizer
  59 |         self.async_reward_fn = AsyncRewardWrapper(reward_fn)
  60 | 
  61 |     async def arun_episode(
  62 |         self,
  63 |         engine: InferenceEngine,
  64 |         data: dict[str, Any],
  65 |     ) -> dict[str, Any] | None | dict[str, InteractionWithTokenLogpReward]:
  66 |         """Run a single episode. MUST be async and non-blocking."""
  67 | 
  68 |         # 1. Prepare input_ids from data
  69 |         input_ids = self.tokenizer.apply_chat_template(
  70 |             data["messages"],
  71 |             tokenize=True,
  72 |             add_generation_prompt=True,
  73 |         )
  74 | 
  75 |         # 2. Build ModelRequest
  76 |         req = ModelRequest(
  77 |             rid=uuid.uuid4().hex,
  78 |             input_ids=list(input_ids),
  79 |             gconfig=self.gconfig.new(n_samples=1),
  80 |             tokenizer=self.tokenizer,
  81 |         )
  82 | 
  83 |         # 3. Generate completion (async)
  84 |         resp: ModelResponse = await engine.agenerate(req)
  85 | 
  86 |         # 4. Compute reward (async)
  87 |         prompt_str = self.tokenizer.decode(input_ids)
  88 |         completion_str = self.tokenizer.decode(resp.output_tokens)
  89 |         reward = await self.async_reward_fn(
  90 |             prompt_str,
  91 |             completion_str,
  92 |             resp.input_tokens,
  93 |             resp.output_tokens,
  94 |             **data,
  95 |         )
  96 | 
  97 |         # 5. Return results in expected format
  98 |         return {
  99 |             "input_ids": torch.tensor(resp.input_tokens),
 100 |             "output_ids": torch.tensor(resp.output_tokens),
 101 |             "reward": torch.tensor(reward),
 102 |         }
 103 | ```
 104 | 
 105 | ### Step 2: Register in __init__.py
 106 | 
 107 | Add to `areal/workflow/__init__.py`:
 108 | 
 109 | ```python
 110 | from areal.workflow.<name> import MyWorkflow
 111 | 
 112 | __all__ = [
 113 |     # ... existing exports
 114 |     "MyWorkflow",
 115 | ]
 116 | ```
 117 | 
 118 | ### Step 3: Update Entry Script
 119 | 
 120 | Update your training script to use the new workflow:
 121 | 
 122 | ```python
 123 | trainer.train(
 124 |     workflow="areal.workflow.<name>.MyWorkflow",
 125 |     # ... other args
 126 | )
 127 | ```
 128 | 
 129 | ### Step 4: Add Tests
 130 | 
 131 | Create `tests/test_<name>_workflow.py`:
 132 | 
 133 | ```python
 134 | import pytest
 135 | from areal.workflow.<name> import MyWorkflow
 136 | 
 137 | @pytest.mark.asyncio
 138 | async def test_workflow_basic():
 139 |     # Test basic functionality
 140 |     pass
 141 | ```
 142 | 
 143 | ## Reference Implementations
 144 | 
 145 | | Workflow           | File                            | Description                |
 146 | | ------------------ | ------------------------------- | -------------------------- |
 147 | | MultiTurnWorkflow  | `areal/workflow/multi_turn.py`  | Multi-turn conversation    |
 148 | | RLVRWorkflow       | `areal/workflow/rlvr.py`        | RL with verifiable rewards |
 149 | | VisionRLVRWorkflow | `areal/workflow/vision_rlvr.py` | Vision + RLVR              |
 150 | 
 151 | ## Key Requirements
 152 | 
 153 | 1. **Async**: `arun_episode` must be `async def` and non-blocking
 154 | 1. **No sync I/O**: Use `aiofiles` for file operations
 155 | 1. **Wrap rewards**: Use `AsyncRewardWrapper` for reward functions
 156 | 1. **Tensor format**: Output tensors should be `[batch, seq_len, ...]`
 157 | 1. **Use helpers**: `concat_padded_tensors` for combining outputs
 158 | 
 159 | ## Common Mistakes
 160 | 
 161 | - Using `open()` instead of `aiofiles.open()`
 162 | - Forgetting to `await` async calls
 163 | - Not wrapping reward function with `AsyncRewardWrapper`
 164 | - Wrong tensor shape conventions
 165 | 
 166 | ______________________________________________________________________
 167 | 
 168 | <!--
 169 | ================================================================================
 170 |                             MAINTAINER GUIDE
 171 | ================================================================================
 172 | 
 173 | Location: .opencode/skills/add-workflow/SKILL.md
 174 | Invocation: /add-workflow <name>
 175 | 
 176 | ## Purpose
 177 | 
 178 | Step-by-step guide for adding new RolloutWorkflow implementations.
 179 | 
 180 | ## How to Update
 181 | 
 182 | ### When Workflow API Changes
 183 | 1. Update the code template in Step 1
 184 | 2. Update the required imports
 185 | 3. Update the method signature if changed
 186 | 
 187 | ### When New Patterns Emerge
 188 | 1. Add to "Reference Implementations" table
 189 | 2. Update "Key Requirements" if new requirements added
 190 | 
 191 | ================================================================================
 192 | -->
```


---
## .opencode/skills/commit-conventions/SKILL.md

```
   1 | ---
   2 | name: commit-conventions
   3 | description: AReaL commit message conventions. MUST load on every git commit -- provides Conventional Commits format with scope inference from file paths.
   4 | ---
   5 | 
   6 | # Commit Conventions
   7 | 
   8 | Commit message conventions and scope inference rules for the AReaL repository.
   9 | 
  10 | ## When to Use
  11 | 
  12 | **ALWAYS load this skill when making any git commit in AReaL.** This includes:
  13 | 
  14 | - Direct commits (`git commit`)
  15 | - Commits during PR creation (`/create-pr`)
  16 | - Commits delegated via `task(load_skills=["commit-conventions"], ...)`
  17 | - Any agent workflow that produces a commit
  18 | 
  19 | ## Commit Message Format
  20 | 
  21 | ```
  22 | <type>(<scope>): <subject>
  23 | 
  24 | <body>
  25 | 
  26 | [Optional sections:]
  27 | Key changes:
  28 | - change 1
  29 | - change 2
  30 | 
  31 | Refs: #123, #456
  32 | ```
  33 | 
  34 | ## Type Selection
  35 | 
  36 | | Type       | When to Use                     |
  37 | | ---------- | ------------------------------- |
  38 | | `feat`     | New feature or capability       |
  39 | | `fix`      | Bug fix                         |
  40 | | `docs`     | Documentation only              |
  41 | | `refactor` | Code change without feature/fix |
  42 | | `test`     | Adding or fixing tests          |
  43 | | `chore`    | Build, deps, config changes     |
  44 | | `perf`     | Performance improvement         |
  45 | 
  46 | ## Scope Inference
  47 | 
  48 | Infer scope from the **primary** changed file paths:
  49 | 
  50 | | File Path Pattern                                            | Scope                          |
  51 | | ------------------------------------------------------------ | ------------------------------ |
  52 | | `areal/workflow/`                                            | `workflow`                     |
  53 | | `areal/engine/`                                              | `engine`                       |
  54 | | `areal/reward/`                                              | `reward`                       |
  55 | | `areal/dataset/`                                             | `dataset`                      |
  56 | | `areal/api/`                                                 | `api`                          |
  57 | | `areal/utils/`                                               | `utils`                        |
  58 | | `areal/infra/`                                               | `infra`                        |
  59 | | `areal/trainer/`                                             | `trainer`                      |
  60 | | `areal/models/`                                              | `models`                       |
  61 | | `areal/experimental/`                                        | `archon`                       |
  62 | | `docs/`                                                      | `docs`                         |
  63 | | `examples/`                                                  | `examples`                     |
  64 | | `AGENTS.md`, `.agents/`, `.claude/`, `.codex/`, `.opencode/` | `agents`                       |
  65 | | Multiple areas                                               | Omit scope or use broader term |
  66 | 
  67 | ## Rules
  68 | 
  69 | - **Subject**: imperative mood, ~50-72 chars, no trailing period
  70 | - **Body**: explain "why" not "what", wrap at 72 chars
  71 | - **Key changes**: bullet list of main modifications (for complex commits with 3+ files)
  72 | - **Refs**: reference issues/PRs if applicable
  73 | 
  74 | ## Examples
  75 | 
  76 | **Single file fix:**
  77 | 
  78 | ```
  79 | fix(reward): handle empty completion in gsm8k
  80 | 
  81 | Return 0 reward instead of raising exception when
  82 | completion string is empty after extraction.
  83 | ```
  84 | 
  85 | **Multi-file feature:**
  86 | 
  87 | ```
  88 | feat(engine): add CPU offload support to ArchonEngine
  89 | 
  90 | Enable torch_memory_saver for model offloading during
  91 | rollout phase to reduce GPU memory pressure.
  92 | 
  93 | Key changes:
  94 | - Add offload/onload methods to ArchonEngine
  95 | - Integrate with weight update flow
  96 | - Handle ROCm compatibility
  97 | ```
  98 | 
  99 | **Docs only:**
 100 | 
 101 | ```
 102 | docs: update algorithm comparison table
 103 | 
 104 | Add SAPO and GSPO to the algorithm family documentation
 105 | with configuration examples.
 106 | ```
 107 | 
 108 | **Agent/tooling changes:**
 109 | 
 110 | ```
 111 | chore(agents): port review-pr command to OpenCode
 112 | 
 113 | Add OpenCode-native commands with task() category
 114 | delegation instead of hardcoded model names.
 115 | 
 116 | Key changes:
 117 | - Create .opencode/command/ with review-pr, create-pr
 118 | - Replace Opus/Sonnet/Haiku with deep/unspecified-high/quick
 119 | - Add expert subagent consultation patterns
 120 | ```
 121 | 
 122 | ______________________________________________________________________
 123 | 
 124 | <!--
 125 | ================================================================================
 126 |                             MAINTAINER GUIDE
 127 | ================================================================================
 128 | 
 129 | Location: .opencode/skills/commit-conventions/SKILL.md
 130 | Invocation: Automatically loaded on every git commit via load_skills
 131 | 
 132 | ## Purpose
 133 | 
 134 | Provides Conventional Commits format with AReaL-specific scope inference
 135 | from file paths. Unlike other skills, this one is NOT user-triggered --
 136 | it is loaded by the system/agent on every commit operation.
 137 | 
 138 | ## How to Update
 139 | 
 140 | ### When New Modules Are Added
 141 | 1. Add the file path pattern and scope to the "Scope Inference" table
 142 | 2. Keep table sorted by areal/ subpackages first, then top-level dirs
 143 | 
 144 | ### When Commit Types Change
 145 | 1. Update the "Type Selection" table
 146 | 2. Add/update examples to illustrate the new type
 147 | 
 148 | ### When Adding Examples
 149 | 1. Each example should demonstrate a distinct commit pattern
 150 | 2. Keep examples realistic -- use actual AReaL module names
 151 | 3. Show both subject-only and subject+body+key-changes variants
 152 | 
 153 | ### Important Design Decisions
 154 | - This skill is ALWAYS loaded (not optional) -- keep it concise to
 155 |   minimize token overhead on every commit
 156 | - Scope inference is path-based, not content-based -- simpler and
 157 |   more deterministic
 158 | - "Multiple areas" -> omit scope rather than invent a new one
 159 | 
 160 | ================================================================================
 161 | -->
```


---
## .opencode/skills/debug-distributed/SKILL.md

```
   1 | ---
   2 | name: debug-distributed
   3 | description: Guide for debugging distributed training issues in AReaL. Use when user encounters hangs, wrong results, OOM, or communication errors.
   4 | ---
   5 | 
   6 | # Debug Distributed Training
   7 | 
   8 | Debugging guide for distributed training issues in AReaL (FSDP2, TP, CP, EP).
   9 | 
  10 | ## When to Use
  11 | 
  12 | This skill is triggered when:
  13 | 
  14 | - Training hangs or deadlocks
  15 | - Results differ across ranks or are numerically wrong
  16 | - OOM errors in distributed settings
  17 | - NCCL/communication errors or device mesh issues
  18 | 
  19 | ## Debugging Principles
  20 | 
  21 | ### Minimal Reproduction
  22 | 
  23 | **Always follow the minimal demo principle**: Reproduce with the least amount of code to
  24 | narrow down the issue faster.
  25 | 
  26 | ```python
  27 | # Bad: Debug in full training loop
  28 | # Good: Create minimal script
  29 | import torch
  30 | import torch.distributed as dist
  31 | 
  32 | dist.init_process_group("nccl")
  33 | rank = dist.get_rank()
  34 | 
  35 | # Reproduce the exact operation that fails
  36 | tensor = torch.ones(10).cuda()
  37 | dist.all_reduce(tensor)  # <-- Isolate the failing op
  38 | print(f"Rank {rank}: {tensor}")
  39 | ```
  40 | 
  41 | **Reduction strategy:**
  42 | 
  43 | 1. Remove unrelated model components
  44 | 1. Use small tensor sizes
  45 | 1. Reduce world_size to minimum (e.g., 2 GPUs)
  46 | 1. Remove torch.compile if possible
  47 | 1. Disable activation checkpointing
  48 | 
  49 | ## Step-by-Step Debugging Guide
  50 | 
  51 | ### 1. Hang Debugging (Deadlocks, Synchronization)
  52 | 
  53 | **Environment Variables for Debugging**:
  54 | 
  55 | ```bash
  56 | # Full debug logging
  57 | export TORCH_DISTRIBUTED_DEBUG=DETAIL
  58 | export NCCL_DEBUG=INFO
  59 | export NCCL_DEBUG_SUBSYS=ALL
  60 | 
  61 | # torch.compile debugging
  62 | export TORCH_LOGS="+dynamo,recompiles"
  63 | export TORCHDYNAMO_VERBOSE=1
  64 | ```
  65 | 
  66 | **Dump Call Stack with py-spy** (for hung processes):
  67 | 
  68 | ```bash
  69 | # Find process IDs
  70 | ps aux | grep python
  71 | 
  72 | # Dump call stack of specific rank
  73 | py-spy dump --pid <PID>
  74 | 
  75 | # Record flame graph for performance analysis
  76 | py-spy record -o profile.svg --pid <PID> --duration 30
  77 | ```
  78 | 
  79 | **Common Causes**:
  80 | 
  81 | 1. **Mismatched Collectives**: One rank calls `all_reduce`, another doesn't.
  82 | 1. **Wrong Process Group**: Using wrong group for collective.
  83 | 1. **Tensor Shape Mismatch**: Different shapes across ranks.
  84 | 
  85 | **Debug Steps**:
  86 | 
  87 | ```python
  88 | # Verify group membership
  89 | mesh = parallel_dims.get_mesh("dp_shard_cp")
  90 | group = mesh.get_group()
  91 | print(f"Rank {dist.get_rank()}: group size = {dist.get_world_size(group)}")
  92 | 
  93 | # Print shapes on all ranks
  94 | print(f"Rank {dist.get_rank()}: tensor.shape = {tensor.shape}")
  95 | dist.barrier()
  96 | ```
  97 | 
  98 | **Timeout Adjustment** (for debugging only):
  99 | 
 100 | ```python
 101 | from areal.engine.core.distributed import patch_dist_group_timeout
 102 | from datetime import timedelta
 103 | patch_dist_group_timeout(timedelta(minutes=30))
 104 | ```
 105 | 
 106 | ### 2. Wrong Results (Gradient, Reduction Issues)
 107 | 
 108 | **Check DTensor Placements**:
 109 | 
 110 | ```python
 111 | from torch.distributed.tensor import DTensor
 112 | if isinstance(param, DTensor):
 113 |     print(f"Param {name}: placements={param.placements}, mesh={param.device_mesh}")
 114 | ```
 115 | 
 116 | **Verify Gradient Reduction**:
 117 | 
 118 | ```python
 119 | for name, param in model.named_parameters():
 120 |     if param.grad is not None:
 121 |         print(f"Rank {dist.get_rank()}: {name} grad_sum = {param.grad.sum().item()}")
 122 | ```
 123 | 
 124 | ### 3. OOM Issues (Memory, Sharding)
 125 | 
 126 | **Check Memory Usage**:
 127 | 
 128 | ```python
 129 | print(f"Rank {dist.get_rank()}: "
 130 |       f"allocated={torch.cuda.memory_allocated()/1e9:.2f}GB, "
 131 |       f"reserved={torch.cuda.memory_reserved()/1e9:.2f}GB")
 132 | ```
 133 | 
 134 | **Check FSDP Coverage**:
 135 | 
 136 | ```python
 137 | for name, param in model.named_parameters():
 138 |     is_dtensor = isinstance(param, DTensor)
 139 |     print(f"{name}: is_dtensor={is_dtensor}, shape={param.shape}")
 140 | ```
 141 | 
 142 | ### 4. Communication Errors
 143 | 
 144 | | Error                     | Cause                | Solution                           |
 145 | | ------------------------- | -------------------- | ---------------------------------- |
 146 | | `NCCL WARN Cuda failure`  | GPU communication    | Check NCCL version, GPU topology   |
 147 | | `RuntimeError: Timed out` | Rank synchronization | Increase timeout, check code paths |
 148 | | `Invalid device mesh`     | Mesh configuration   | Verify world_size = dp * tp * cp   |
 149 | 
 150 | ## Debugging Tools
 151 | 
 152 | ### Environment Variables Reference
 153 | 
 154 | | Variable                          | Purpose                                |
 155 | | --------------------------------- | -------------------------------------- |
 156 | | `TORCH_DISTRIBUTED_DEBUG=DETAIL`  | Detailed distributed logging           |
 157 | | `NCCL_DEBUG=INFO`                 | NCCL communication logging             |
 158 | | `NCCL_DEBUG_SUBSYS=ALL`           | All NCCL subsystems                    |
 159 | | `TORCH_LOGS="+dynamo,recompiles"` | torch.compile logging                  |
 160 | | `TORCHDYNAMO_VERBOSE=1`           | Dynamo verbose output                  |
 161 | | `CUDA_LAUNCH_BLOCKING=1`          | Synchronous CUDA (slow, for debugging) |
 162 | 
 163 | ### py-spy for Call Stack Analysis
 164 | 
 165 | ```bash
 166 | # Install
 167 | pip install py-spy
 168 | 
 169 | # Dump call stack of hung process
 170 | py-spy dump --pid <PID>
 171 | 
 172 | # Dump all Python processes
 173 | pgrep -f python | xargs -I {} py-spy dump --pid {}
 174 | 
 175 | # Record flame graph
 176 | py-spy record -o profile.svg --pid <PID> --duration 30
 177 | ```
 178 | 
 179 | ### Rank-Conditional Printing
 180 | 
 181 | ```python
 182 | def print_all_ranks(msg):
 183 |     for r in range(dist.get_world_size()):
 184 |         if dist.get_rank() == r:
 185 |             print(f"[Rank {r}] {msg}")
 186 |         dist.barrier()
 187 | ```
 188 | 
 189 | ### Check Device Mesh
 190 | 
 191 | ```python
 192 | def debug_mesh(parallel_dims):
 193 |     mesh = parallel_dims.world_mesh
 194 |     for dim_name in mesh.mesh_dim_names:
 195 |         submesh = parallel_dims.get_mesh(dim_name)
 196 |         if submesh:
 197 |             print(f"Rank {dist.get_rank()}: {dim_name} size={submesh.size()}")
 198 | ```
 199 | 
 200 | ### Validate Tensor Consistency
 201 | 
 202 | ```python
 203 | def check_tensor_consistency(tensor, name, group=None):
 204 |     local_sum = tensor.sum().item()
 205 |     tensor_sums = [None] * dist.get_world_size(group)
 206 |     dist.all_gather_object(tensor_sums, local_sum, group=group)
 207 |     if dist.get_rank() == 0 and len(set(tensor_sums)) > 1:
 208 |         print(f"WARNING: {name} inconsistent: {tensor_sums}")
 209 | ```
 210 | 
 211 | ## Key Files Reference
 212 | 
 213 | | Component       | File                                                          |
 214 | | --------------- | ------------------------------------------------------------- |
 215 | | Parallel Dims   | `areal/experimental/models/archon/parallel_dims.py`           |
 216 | | Expert Parallel | `areal/experimental/models/archon/expert_parallel.py`         |
 217 | | Ulysses (CP)    | `areal/experimental/models/archon/ulysses.py`                 |
 218 | | FSDP/TP Apply   | `areal/experimental/models/archon/qwen2/infra/parallelize.py` |
 219 | 
 220 | ______________________________________________________________________
 221 | 
 222 | <!--
 223 | ================================================================================
 224 |                             MAINTAINER GUIDE
 225 | ================================================================================
 226 | 
 227 | Location: .opencode/skills/debug-distributed/SKILL.md
 228 | Invocation: /debug-distributed
 229 | 
 230 | ## Purpose
 231 | 
 232 | Debugging guide for distributed training issues.
 233 | Covers FSDP2, Tensor Parallelism, Context Parallelism, and Expert Parallelism.
 234 | 
 235 | ## How to Update
 236 | 
 237 | ### When Adding New Parallelism Features
 238 | 1. Add section for the parallelism type
 239 | 2. Document common error patterns and debugging snippets
 240 | 
 241 | ### When PyTorch Distributed APIs Change
 242 | 1. Update DTensor/DeviceMesh examples
 243 | 2. Update environment variable references
 244 | 
 245 | ### When New Error Patterns Emerge
 246 | 1. Add to "Common Errors and Solutions" table
 247 | 2. Reference relevant source files
 248 | 
 249 | ================================================================================
 250 | -->
```


---
## AGENTS.md

```
   1 | <!-- Go-to brief for AI coding agents working on AReaL. -->
   2 | 
   3 | # AGENTS.md -- AReaL Agent Operations Guide
   4 | 
   5 | ## Quick reference
   6 | 
   7 | **Tech stack**: Python 3.12+ | PyTorch | FSDP2 / Megatron / Archon | SGLang / vLLM
   8 | 
   9 | ```bash
  10 | # Environment
  11 | uv sync --extra cuda            # CUDA + SGLang inference (default); for vLLM: --extra cuda-vllm
  12 | source .venv/bin/activate        # activate venv BEFORE pre-commit or git commit if venv exists
  13 | pre-commit install --install-hooks  # hooks: Ruff, clang-format, mdformat, nbstripout, conventional-commits
  14 | pre-commit run --all-files       # lint + format everything
  15 | 
  16 | # Tests
  17 | uv run pytest tests/test_<topic>.py
  18 | 
  19 | # CLI docs
  20 | uv run python docs/generate_cli_docs.py
  21 | 
  22 | # Docs build (canonical, release-aligned)
  23 | ./docs/build_all.sh
  24 | # Do NOT use `jupyter-book build docs/en|docs/zh` directly for final preview/release,
  25 | # because it skips AReaL-specific static setup and output packaging.
  26 | ```
  27 | 
  28 | **Hard rules** -- never violate:
  29 | 
  30 | - No wildcard imports (`from x import *`).
  31 | - No hardcoded secrets, paths, or endpoints.
  32 | - No skipping pre-commit hooks.
  33 | - No guessing cluster configs or rebuilding CUDA/driver stacks.
  34 | - Integration tests require multi-node hardware -- explain skips explicitly.
  35 | 
  36 | **Always do**:
  37 | 
  38 | - Read relevant files before modifying code.
  39 | - Run `pre-commit run --all-files` before committing.
  40 | - Follow existing code patterns in the same module.
  41 | - Add tests for new functionality.
  42 | - Ask for decisions and clarifications with short, structured options instead of broad
  43 |   open-ended questions. Use the platform's native question/clarification tool if
  44 |   available.
  45 | 
  46 | **Ask first** before:
  47 | 
  48 | - Modifying config structures in `areal/api/cli_args.py`.
  49 | - Adding new dependencies.
  50 | - Changing launcher or scheduler logic.
  51 | - Deleting or renaming public APIs.
  52 | 
  53 | When unsure, leave a `TODO(agent)` comment and note the constraint in your response.
  54 | 
  55 | ______________________________________________________________________
  56 | 
  57 | ## Repository map
  58 | 
  59 | ```
  60 | areal/                     Core Python package
  61 | |-- api/                   Config dataclasses, contracts, IO structs
  62 | |-- dataset/               Stateful dataset loaders (GSM8K, Geometry3K, CLEVR, ...)
  63 | |-- engine/                Training backends (FSDP2, Megatron) + inference adapters
  64 | |-- experimental/          Prototype engines/workflows (Archon MoE engine)
  65 | |-- infra/                 Launchers (Local/Ray/Slurm), schedulers, utilities
  66 | |-- models/                Model adapters (Megatron-Core, Transformers, custom heads)
  67 | |-- reward/                Built-in reward functions + math parsers
  68 | |-- tests/                 Unit/integration test suites
  69 | |-- trainer/               High-level orchestrators (PPOTrainer, SFTTrainer)
  70 | |-- utils/                 Cross-cutting helpers (logging, data, checkpoints, RL ops)
  71 | +-- workflow/              RolloutWorkflow implementations (RLVR, multi-turn, vision)
  72 | 
  73 | docs/                      Jupyter Book docs (https://inclusionai.github.io/AReaL/)
  74 | examples/                  Training scripts and launcher recipes
  75 | ```
  76 | 
  77 | ______________________________________________________________________
  78 | 
  79 | ## Code style & patterns
  80 | 
  81 | - **Composition over inheritance** -- keep hierarchies \<= 2 levels; prefer delegation.
  82 | 
  83 | | Type             | Pattern         | Example                                   |
  84 | | ---------------- | --------------- | ----------------------------------------- |
  85 | | Config dataclass | `XxxConfig`     | `GRPOConfig`, `FSDPEngineConfig`          |
  86 | | Engine class     | `XxxEngine`     | `FSDPEngine`, `ArchonEngine`              |
  87 | | Workflow class   | `XxxWorkflow`   | `RLVRWorkflow`, `MultiTurnWorkflow`       |
  88 | | Reward function  | `xxx_reward_fn` | `gsm8k_reward_fn`, `geometry3k_reward_fn` |
  89 | 
  90 | **Logging**: `areal.utils.logging.getLogger(name)` with **PascalCase** names -- never
  91 | `print` or `logging.__name__`. Per-rank format: `[{Component} Rank {N}]`. Register new
  92 | loggers with color in `areal/utils/logging.py`.
  93 | 
  94 | **Performance**:
  95 | 
  96 | - No GPU-CPU sync in hot paths (`.item()`, `.tolist()`, `print(tensor)`).
  97 | - Batch ops over Python loops on tensor elements.
  98 | - Explicit `dtype`/`device`; `torch.Size` assertions for shape validation.
  99 | 
 100 | **Typing & imports**: explicit type hints; reuse `areal/api/cli_args.py` dataclasses; no
 101 | wildcard imports; heavy optional deps inside functions.
 102 | 
 103 | **Async**: rollout workflows must stay non-blocking (`await` + `aiofiles`); no sync I/O
 104 | in `arun_episode`.
 105 | 
 106 | ______________________________________________________________________
 107 | 
 108 | ## Domain experts & skills
 109 | 
 110 | Fire the appropriate **expert subagent** or **load a skill** based on what you're
 111 | working on. Experts are read-only consultants with deep domain knowledge; skills are
 112 | step-by-step implementation guides.
 113 | 
 114 | | Working on...                | Fire subagent      | Load skill          |
 115 | | ---------------------------- | ------------------ | ------------------- |
 116 | | FSDP engine code             | `fsdp-expert`      | --                  |
 117 | | Archon engine / new model    | `archon-expert`    | `add-archon-model`  |
 118 | | Megatron engine code         | `megatron-expert`  | --                  |
 119 | | RL algorithms / PPO / GRPO   | `algorithm-expert` | --                  |
 120 | | Launcher / scheduler / infra | `launcher-expert`  | `debug-distributed` |
 121 | | New reward function          | --                 | `add-reward`        |
 122 | | New dataset loader           | --                 | `add-dataset`       |
 123 | | New rollout workflow         | --                 | `add-workflow`      |
 124 | | Unit tests                   | --                 | `add-unit-tests`    |
 125 | | Distributed debugging        | --                 | `debug-distributed` |
 126 | 
 127 | **How to invoke experts and skills** (platform-specific):
 128 | 
 129 | | Platform | Fire expert subagent                                                               | Load skill                                         |
 130 | | -------- | ---------------------------------------------------------------------------------- | -------------------------------------------------- |
 131 | | OpenCode | `task(subagent_type="<name>", load_skills=[], run_in_background=true, prompt="…")` | `skill(name="<name>")` or `load_skills=["<name>"]` |
 132 | | Codex    | Invoke registered subagent by canonical name (see `.codex/config.toml`)            | Reference `.agents/skills/<name>/SKILL.md`         |
 133 | 
 134 | **Harness layout**:
 135 | 
 136 | | Component         | OpenCode                                | Codex                                                  |
 137 | | ----------------- | --------------------------------------- | ------------------------------------------------------ |
 138 | | Root instructions | `AGENTS.md`                             | `AGENTS.md`                                            |
 139 | | Agent configs     | `.opencode/agents/*.md` (frontmatter)   | `.codex/config.toml` + `.codex/agents/*.toml` + `*.md` |
 140 | | Skills            | `.opencode/skills/` + `.agents/skills/` | `.agents/skills/<name>/SKILL.md`                       |
 141 | 
 142 | Directly executable workflows (both platforms): `add-workflow`, `review-pr`,
 143 | `create-pr`, `translate-doc-zh`.
 144 | 
 145 | ______________________________________________________________________
 146 | 
 147 | ## Core concepts
 148 | 
 149 | **Trainer** orchestrator (`areal/trainer/`, `PPOTrainer`, `SFTTrainer`): manages the
 150 | training loop, dataset loading, and workflow execution. Entry point:
 151 | `examples/math/gsm8k_rl.py`.
 152 | 
 153 | **Rollout workflows** (`areal/workflow/`, `RolloutWorkflow.arun_episode`): define how
 154 | episodes are generated. Use `add-workflow` skill for step-by-step guide.
 155 | 
 156 | **Engines**: *Inference engines* handle async generation via `engine.agenerate()` and
 157 | manage weight updates. *Training engines* consume rollout tensors, compute PPO/GRPO
 158 | updates, and broadcast weight versions (FSDP2, Megatron, or Archon).
 159 | 
 160 | **Weight versioning**: async workflows require version alignment via `WeightUpdateMeta`
 161 | (`areal/api/engine_api.py`). Critical for correctness across distributed training.
 162 | 
 163 | **Observability**: emit metrics via `stats_tracker.get()`, persist artifacts under
 164 | `dump_dir`, checkpoint via `areal/utils/saver.py` / `recover.py`.
 165 | 
 166 | **Launcher / scheduler**: training requires cluster setup (local / Ray / Slurm) via
 167 | configs in `areal/infra/launcher/`. See `launcher-expert` for deployment guidance.
 168 | 
 169 | ______________________________________________________________________
 170 | 
 171 | ## API & config rules
 172 | 
 173 | *Applies to: `areal/api/**`*
 174 | 
 175 | - **Field ordering**: required -> common optional -> rare optional -> internal (`_`
 176 |   prefix).
 177 | - **Validation**: `__post_init__` with `ValueError` and clear message.
 178 | - **Backward compat**: add fields with defaults; deprecate before removing; avoid type
 179 |   changes.
 180 | - **CLI**: use `Literal` for enum choices; all public configs need docstrings with
 181 |   constraints.
 182 | 
 183 | ______________________________________________________________________
 184 | 
 185 | ## Distributed code rules
 186 | 
 187 | *Applies to: `areal/engine/**`, `areal/experimental/**`*
 188 | 
 189 | - Never create global process groups at module level; always pass `process_group`
 190 |   explicitly.
 191 | - `dist.get_rank(group)` not `dist.get_rank()` when group matters.
 192 | - DeviceMesh dimensions must match `ArchonParallelDims`: `dp_shard`, `tp`, `cp`, `ep`,
 193 |   `etp`.
 194 | - All-reduce: all ranks must call. Broadcast: explicit `src`. Barrier: debugging only.
 195 | 
 196 | | Issue         | Cause                            | Fix                       |
 197 | | ------------- | -------------------------------- | ------------------------- |
 198 | | Hang          | Mismatched collective calls      | All ranks call same op    |
 199 | | Wrong results | Incorrect `ReduceOp`             | Check SUM vs MEAN         |
 200 | | OOM           | Unsharded tensor on wrong device | Verify DTensor placements |
 201 | 
 202 | Debug env vars: `TORCH_DISTRIBUTED_DEBUG=DETAIL`, `NCCL_DEBUG=INFO`,
 203 | `CUDA_LAUNCH_BLOCKING=1`. See the `debug-distributed` skill for the full workflow.
 204 | 
 205 | ______________________________________________________________________
 206 | 
 207 | ## Testing rules
 208 | 
 209 | *Applies to: `**/tests/**`, `test_*.py`*
 210 | 
 211 | | Marker                                  | When                             |
 212 | | --------------------------------------- | -------------------------------- |
 213 | | `@pytest.mark.slow`                     | > 10s (excluded from default CI) |
 214 | | `@pytest.mark.slow` + `@pytest.mark.ci` | Slow but must run in CI          |
 215 | | `@pytest.mark.asyncio`                  | Async tests                      |
 216 | 
 217 | - Naming: `test_<what>_<condition>_<expected>()` with Arrange/Act/Assert.
 218 | - GPU: skip gracefully (`@pytest.mark.skipif(not CUDA_AVAILABLE, reason="...")`).
 219 | - Distributed mocking: `torch.distributed.fake_pg`; don't mock FSDP/DTensor internals.
 220 | - Assertions: `torch.testing.assert_close()` with explicit `rtol`/`atol`; prefer
 221 |   `tmp_path`, `monkeypatch`.
 222 | 
 223 | | Suite       | Command                       | GPU       |
 224 | | ----------- | ----------------------------- | --------- |
 225 | | Unit        | `pytest tests/test_*.py`      | No        |
 226 | | GRPO        | `pytest tests/grpo/`          | Yes       |
 227 | | FSDP        | `pytest tests/test_fsdp_*.py` | Yes       |
 228 | | Distributed | `pytest tests/torchrun/`      | Multi-GPU |
 229 | 
 230 | ______________________________________________________________________
 231 | 
 232 | ## Collaboration & review
 233 | 
 234 | - **Branches**: kebab-case (`feature/multi-turn-metrics`, `bugfix/fsdp-weight-sync`).
 235 | - **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`), ~72 char subject,
 236 |   imperative voice. Squash WIP before PR.
 237 | - **Pre-merge**: full pre-commit stack; doc-only edits need at least `mdformat --check`.
 238 | - **PRs**: tie to issue, highlight risk areas, list test commands executed, note skipped
 239 |   suites with reasons.
 240 | 
 241 | | Skill                | Purpose                                                |
 242 | | -------------------- | ------------------------------------------------------ |
 243 | | `create-pr`          | Rebase, squash, and create or update a PR              |
 244 | | `commit-conventions` | Commit message conventions to load before `git commit` |
 245 | | `review-pr`          | Dynamic PR review with targeted expert consultation    |
 246 | | `translate-doc-zh`   | Translate English docs to Chinese                      |
 247 | 
 248 | ______________________________________________________________________
 249 | 
 250 | ## Reference material
 251 | 
 252 | - **Docs portal**: <https://inclusionai.github.io/AReaL/>
 253 | - **Quickstart**: `docs/tutorial/quickstart.md`
 254 | - **Architecture**: `docs/tutorial/gsm8k_grpo.md`
 255 | - **Customization**: `docs/customization/*.md`
 256 | - **Algorithms**: `docs/algorithms/*.md`
 257 | - **Best practices**: `docs/best_practices/*.md`
 258 | - **CLI reference**: `docs/cli_reference.md`
 259 | - **Agent workflow**: `docs/customization/agent.md`
```


---
## CLAUDE.md

```
   1 | # CLAUDE.md - AReaL
   2 | 
   3 | ## WHAT: Project Overview
   4 | 
   5 | AReaL is a distributed RL training framework for LLM alignment via reinforcement
   6 | learning.
   7 | 
   8 | **Tech Stack**: Python 3.12+ | PyTorch | FSDP2/Megatron | SGLang/vLLM
   9 | 
  10 | **Core Directories**:
  11 | 
  12 | - `areal/` - Core package
  13 |   - `api/` - Config dataclasses, workflow/engine contracts
  14 |   - `engine/` - FSDP2, Megatron, SGLang/vLLM adapters
  15 |     - `fsdp_utils/` - FSDP2-specific utilities (checkpoint, grad, optimizer, parallel)
  16 |     - `megatron_utils/` - Megatron/FP8 utilities (checkpoint, pipeline, quantization)
  17 |     - `core/` - Engine-shared utilities (distributed, lock, model, offload)
  18 |   - `infra/` - Infrastructure (launcher, scheduler, RPC)
  19 |     - `utils/` - Infrastructure utilities (launcher, proc, http, concurrent, slurm, ray)
  20 |   - `workflow/` - RolloutWorkflow implementations
  21 |   - `reward/` - Reward functions
  22 |   - `dataset/` - Dataset loaders
  23 |   - `utils/` - Cross-cutting utilities (logging, data, checkpoints, network, RL
  24 |     functional)
  25 | - `examples/` - Training scripts and configs
  26 | - `docs/` - Jupyter Book source
  27 | 
  28 | ## WHY: Purpose
  29 | 
  30 | - Enable efficient RL training for LLM alignment at scale
  31 | - Async rollout + distributed training for high throughput
  32 | - Modular design: workflows, engines, rewards, and datasets are independently extensible
  33 | 
  34 | ## HOW: Core Commands
  35 | 
  36 | ```bash
  37 | # Check environment
  38 | python --version              # Requires 3.12+
  39 | uv --version                  # Install: https://docs.astral.sh/uv/
  40 | 
  41 | # Sync dependencies
  42 | uv sync --extra cuda          # CUDA + SGLang inference (default)
  43 | uv sync --group dev           # Include dev/test packages
  44 | uv run python3 areal/tools/validate_installation.py  # Validate installation
  45 | 
  46 | # Pre-commit hooks
  47 | pre-commit install --install-hooks  # Set up hooks (run once)
  48 | pre-commit run --all-files    # Format and lint
  49 | 
  50 | # Run tests
  51 | # First check GPU availability (many tests require GPU)
  52 | python -c "import torch; print('GPU available:', torch.cuda.is_available())"
  53 | uv run pytest tests/test_<topic>.py
  54 | 
  55 | # Generate CLI docs
  56 | uv run python docs/generate_cli_docs.py
  57 | 
  58 | # Build docs (canonical, release-aligned)
  59 | ./docs/build_all.sh
  60 | # Do NOT use `jupyter-book build docs/en|docs/zh` directly for final preview/release,
  61 | # because it skips AReaL-specific static setup and output packaging.
  62 | ```
  63 | 
  64 | ## Boundaries
  65 | 
  66 | ### Constraints
  67 | 
  68 | - Designed for distributed GPU clusters; assume containerized execution
  69 | - Integration tests require multi-node hardware; explain skips when unavailable
  70 | - Secrets and endpoints are managed outside the repo
  71 | 
  72 | ### Always Do
  73 | 
  74 | - Read relevant files before modifying code
  75 | - Run `pre-commit run --all-files` before committing
  76 | - Follow existing code patterns in the same module
  77 | - Add tests for new functionality
  78 | 
  79 | ### Ask First
  80 | 
  81 | - Modifying config structures in `areal/api/cli_args.py`
  82 | - Adding new dependencies
  83 | - Changing launcher or scheduler logic
  84 | - Deleting or renaming public APIs
  85 | - Running GPU/distributed tests (check GPU first:
  86 |   `python -c "import torch; print('GPU available:', torch.cuda.is_available())"`)
  87 | 
  88 | ### Never Do
  89 | 
  90 | - Hardcode secrets, paths, or endpoints
  91 | - Skip pre-commit hooks
  92 | - Guess cluster configs or rebuild CUDA/driver stacks
  93 | - Use wildcard imports (`from x import *`)
  94 | 
  95 | ## Progressive Disclosure: Detailed Guides
  96 | 
  97 | | Task                   | Reference                                                     |
  98 | | ---------------------- | ------------------------------------------------------------- |
  99 | | Add Workflow           | `docs/customization/agent.md`, `areal/workflow/multi_turn.py` |
 100 | | Add Dataset            | `docs/customization/`, `areal/dataset/gsm8k.py`               |
 101 | | Add Reward             | `areal/api/reward_api.py`, `areal/reward/geometry3k.py`       |
 102 | | Add Archon Model       | `areal/experimental/models/archon/qwen2/`, `qwen3/`           |
 103 | | Algorithm Details      | `docs/algorithms/*.md`                                        |
 104 | | Quickstart             | `docs/tutorial/quickstart.md`                                 |
 105 | | Architecture Deep Dive | `docs/tutorial/gsm8k_grpo.md`                                 |
 106 | | CLI Reference          | `docs/cli_reference.md`                                       |
 107 | 
 108 | ## Git Workflow
 109 | 
 110 | - **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`), ~72 chars subject,
 111 |   imperative voice, reasoning in body
 112 | - **Squash**: Squash WIP commits before opening PR
 113 | - **PR requirements**: Run pre-commit, document test coverage, note hardware limitations
 114 | 
 115 | ## Extended Configuration
 116 | 
 117 | See `.claude/agents/`, `.claude/skills/`, `.claude/commands/`, and `.claude/rules/` for
 118 | specialized instructions.
 119 | 
 120 | ### Agents
 121 | 
 122 | | Agent                       | Purpose                                   | Activation Trigger                                                  |
 123 | | --------------------------- | ----------------------------------------- | ------------------------------------------------------------------- |
 124 | | `planner`                   | Implementation planning                   | Before multi-file changes, new features, or architectural decisions |
 125 | | `simple-code-reviewer`      | Quick code quality checks                 | After code changes, before committing                               |
 126 | | `code-verifier`             | Formatting/linting/tests                  | After code changes, before committing                               |
 127 | | `fsdp-engine-expert`        | FSDPEngine implementation                 | FSDPEngine code changes or questions                                |
 128 | | `archon-engine-expert`      | ArchonEngine implementation               | ArchonEngine code changes or questions                              |
 129 | | `megatron-engine-expert`    | MegatronEngine implementation             | MegatronEngine code changes or questions                            |
 130 | | `algorithm-expert`          | RL algorithms                             | GRPO/PPO/DAPO questions                                             |
 131 | | `launcher-scheduler-expert` | Cluster launching and resource scheduling | Launcher/scheduler code changes or configuration questions          |
 132 | 
 133 | **Stage-by-Stage Agent Guidance**:
 134 | 
 135 | 1. **Planning Stage** (Before coding): Use `planner` for architecture design and
 136 |    implementation planning
 137 | 1. **Code Formatting & Linting** (After coding): Use `code-verifier` to automatically
 138 |    run formatting, linting, and tests, catching syntax errors and style issues quickly
 139 | 1. **Code Quality Check** (After formatting): Use `simple-code-reviewer` for quick code
 140 |    quality checks, focusing on logic issues and code smells
 141 | 
 142 | ### Skills (Guided Development Workflows)
 143 | 
 144 | Skills provide step-by-step guides for common development tasks:
 145 | 
 146 | - `/add-dataset` - Dataset loader creation guide
 147 | - `/add-workflow` - Workflow implementation guide
 148 | - `/add-reward` - Reward function guide
 149 | - `/add-archon-model` - Archon engine model architecture guide
 150 | - `/debug-distributed` - Distributed debugging guide
 151 | - `/add-unit-tests` - Test development guide (NEW)
 152 | 
 153 | ### Commands (User-invoked Actions)
 154 | 
 155 | Commands perform specific actions when invoked:
 156 | 
 157 | - `/create-pr` - Rebase, squash commits, and create/update PR with intelligent messages
 158 | - `/gen-commit-msg` - Generate commit messages from staged changes
 159 | - `/review-pr` - Intelligent PR code review with dynamic agent allocation
 160 | - `/translate-doc-zh` - Translate English documentation to Chinese
 161 | 
 162 | ### Rules (Code Quality Standards)
 163 | 
 164 | Project-wide standards enforced across all code changes:
 165 | 
 166 | - `api-config.md` - Configuration dataclass design patterns
 167 | - `code-style.md` - Coding conventions beyond pre-commit hooks
 168 | - `distributed.md` - Distributed training patterns and constraints
 169 | - `testing.md` - Testing strategy and coverage requirements
```


---
## README.md

```
   1 | <h1 align="center">
   2 | <em>AReaL</em>: A Large-Scale Asynchronous Reinforcement Learning System
   3 | </h1>
   4 | 
   5 | <p align="center">
   6 | | <a href="https://arxiv.org/pdf/2505.24298"><b>Paper</b></a> | <a href="https://inclusionai.github.io/AReaL/"><b>Documentation</b></a> | <a href="https://inclusionai.github.io/AReaL/zh/"><b>中文文档</b></a> | <a href="https://deepwiki.com/inclusionAI/AReaL"><b>Ask DeepWiki</b></a> | <a href="https://huggingface.co/collections/inclusionAI/"><b>🤗 Models & Data</b></a> |
   7 | <a href="./assets/wechat_qrcode.png" target="_blank"><img src="./assets/wechat_icon.png" width="20" style="vertical-align: middle;"> <b>WeChat (微信) Group</b></a> |
   8 |   <a href="https://gitcgr.com/inclusionAI/AReaL">
   9 |     <img src="https://gitcgr.com/badge/inclusionAI/AReaL.svg" alt="gitcgr" />
  10 |   </a>
  11 | </p>
  12 | 
  13 | <img align="right" alt="ReaL" src="/assets/logo.png" width="20%">
  14 | 
  15 | AReaL is an open-source **fully asynchronous** reinforcement learning training system
  16 | for large **reasoning and agentic models**, developed by members from Tsinghua IIIS and
  17 | the AReaL Team at Ant Group. Built upon the open-source project
  18 | [ReaLHF](https://github.com/openpsi-project/ReaLHF), we are fully committed to
  19 | open-source principles by providing the training details, data, and infrastructure
  20 | required to reproduce our results, along with the models themselves. AReaL aims to help
  21 | everyone build their own AI agents easily and affordably. Our team loves milk tea
  22 | because it's delicious, customizable, and affordable—we hope you enjoy our project just
  23 | as much as you'd enjoy real milk tea. Cheers!
  24 | 
  25 | **AReaL Highlights**
  26 | 
  27 | - ⚡ **Flexibility**: Seamless customization for
  28 |   [agentic RL](https://inclusionai.github.io/AReaL/en/tutorial/agentic_rl.html) and
  29 |   [online RL training](./examples/openclaw/) by simply replacing the `base_url`.
  30 | - 📈 **Scalability**: **Stable** fully asynchronous RL training with **industry-leading
  31 |   speed**.
  32 | - ✨ **Cutting-Edge Performance**: State-of-the-art [math](/blog/AReaL_v0_2.md),
  33 |   [coding](/blog/AReaL_v0_3.md), [search](https://github.com/inclusionAI/ASearcher), and
  34 |   [customer service](https://arxiv.org/abs/2601.22607) agents.
  35 | 
  36 | ## 📰 News
  37 | 
  38 | **\[2026/03/02\]** We provide [a complete example](./examples/openclaw/) to train your
  39 | own 🦞 OpenClaw agent by simply replacing the `base_url` and `api_key` with AReaL's RL
  40 | service - no complicated dependencies, no code changes, works with any agentic runtime!
  41 | 
  42 | **\[2026/02/06\]** We are delighted to introduce **AReaL-SEA**, a self-evolving data
  43 | synthesis engine. Combined with RL training on AReaL, the 235B MoE model surpasses GPT 5
  44 | and achieves comparable performance with Gemini 3.0 Pro on $\\tau^2$-bench! Check out
  45 | the [paper](https://arxiv.org/pdf/2601.22607),
  46 | [model](https://huggingface.co/inclusionAI/AReaL-SEA-235B-A22B),
  47 | [data](https://huggingface.co/datasets/inclusionAI/AReaL-tau2-data), and
  48 | [code](https://github.com/inclusionAI/AReaL/tree/main/examples/tau2).
  49 | 
  50 | **\[2026/01/15\]** Congrats to our friends at [CAMEL-AI](https://www.camel-ai.org/) for
  51 | open-sourcing [SETA](https://github.com/camel-ai/seta), their terminal agent RL project
  52 | trained with AReaL! Check out
  53 | [their training workflow](https://github.com/camel-ai/seta/tree/main/training/tbench_areal_workflow)
  54 | and the [announcement on X](https://x.com/guohao_li/status/2009678513574408636).
  55 | 
  56 | <details>
  57 | <summary><b>📋 Previous Releases</b></summary>
  58 | 
  59 | **\[2026/01/01\]** Happy New Year! Thanks to the outstanding contribution from
  60 | @HwVanICI, we are excited to officially announce stable support for AReaL training on
  61 | **Ascend NPU devices**! The code is actively maintained and continuously updated in the
  62 | [`ascend` branch](https://github.com/inclusionAI/AReaL/tree/ascend). Check out
  63 | [our documentation](https://inclusionai.github.io/AReaL/en/tutorial/installation_npu.html)
  64 | to get started, and feel free to report any issues!
  65 | 
  66 | **\[2025/08/30\]** Introducing ASearcher, a state-of-the-art search agent built with
  67 | AReaL's end-to-end asynchronous RL training. Check out the [paper](assets/paper.pdf) and
  68 | the [open-source repository](https://github.com/inclusionAI/ASearcher)!
  69 | 
  70 | **\[2025/07/31\] (AReaL-lite)** We introduce AReaL-lite, a **lightweight** version of
  71 | AReaL designed specifically for AI researchers and rapid prototyping. AReaL-lite
  72 | features an **algorithm-first** API design that prioritizes ease of use and algorithm
  73 | development, while natively supporting **fully asynchronous agentic RL**. With 80% fewer
  74 | lines of code, AReaL-lite maintains 90% of AReaL's performance and core functionality.
  75 | Check out [our AReaL-lite design documentation](/areal/README.md) and
  76 | [the quickstart guide](https://inclusionai.github.io/AReaL/en/tutorial/quickstart.html)
  77 | to begin your journey with **AReaL-lite**!
  78 | 
  79 | **\[2025/06/03\] (v0.3, boba²)** We release **boba²** (double-boba) for fully
  80 | asynchronous RL training, which achieves **2.77× speedup while delivering comparable or
  81 | superior training performance** compared to synchronous systems. Furthermore,
  82 | asynchronous RL significantly simplifies multi-turn agentic RL training setup! Check out
  83 | [our v0.3 overview blog](/blog/AReaL_v0_3.md) and the
  84 | [research paper](assets/paper.pdf).
  85 | 
  86 | **\[2025/03/31\] (v0.2, boba)** Introducing our milestone release—boba! Please call it
  87 | A-ReaL-boba! This release features significantly faster training with SGLang support and
  88 | state-of-the-art 7B and 32B models for mathematical reasoning. Check out our
  89 | [v0.2 technical blog](/blog/AReaL_v0_2.md).
  90 | 
  91 | **\[2025/02/24\] (v0.1)** Our initial release includes reproducible results for 1.5B and
  92 | 7B Large Reasoning Models (LRMs). Check out our
  93 | [v0.1 technical blog](/blog/AReaL_v0_1.md).
  94 | 
  95 | </details>
  96 | 
  97 | ## 🚀 Getting Started
  98 | 
  99 | First, install the package:
 100 | 
 101 | ```bash
 102 | git clone https://github.com/inclusionAI/AReaL
 103 | cd AReaL
 104 | pip install uv
 105 | # Install flash-attn pre-built wheel first to avoid compiling from source
 106 | # (pick the wheel matching your Python version; see https://github.com/mjun0812/flash-attention-prebuild-wheels/releases)
 107 | uv pip install "https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.7.16/flash_attn-2.8.3+cu128torch2.9-cp312-cp312-linux_x86_64.whl"
 108 | uv sync --extra cuda  # installs training packages + SGLang (default inference backend)
 109 | ```
 110 | 
 111 | Our training scripts automatically download the required dataset (openai/gsm8k) and
 112 | model (Qwen/Qwen2-1.5B-Instruct). To run on a single node:
 113 | 
 114 | ```bash
 115 | python3 examples/math/gsm8k_rl.py --config examples/math/gsm8k_grpo.yaml scheduler.type=local
 116 | ```
 117 | 
 118 | To run on a Ray cluster with 2 nodes and 8 GPUs per node (remember to update paths in
 119 | the YAML file to point to your shared storage):
 120 | 
 121 | ```bash
 122 | python3 examples/math/gsm8k_rl.py --config examples/math/gsm8k_grpo.yaml \
 123 |   cluster.n_nodes=2 cluster.n_gpus_per_node=8 \
 124 |   scheduler.type=ray
 125 | ```
 126 | 
 127 | For comprehensive setup instructions, see
 128 | [our quickstart guide](https://inclusionai.github.io/AReaL/en/tutorial/quickstart.html).
 129 | 
 130 | ## 📚 Examples
 131 | 
 132 | ### Math & Reasoning
 133 | 
 134 | | Task                                                | Description                                                                                  | Performance                                                       |
 135 | | --------------------------------------------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
 136 | | **[Math](examples/math/)**                          | GSM8K math reasoning with GRPO, PPO, DAPO, REINFORCE, RLOO, LitePPO, DR-GRPO, GSPO, and more | -                                                                 |
 137 | | **[Multi-Turn Math](examples/multi_turn_math/)**    | Multi-turn math agent with reward discounting across turns                                   | [Training Curve](examples/multi_turn_math/reward_curve.png)       |
 138 | | **[LoRA Math](examples/math/gsm8k_grpo_lora.yaml)** | Parameter-efficient math training with LoRA (SGLang/vLLM backends)                           | -                                                                 |
 139 | | **[Countdown](examples/countdown/)**                | Countdown numbers game with custom rewards                                                   | [Training Curve](examples/countdown/countdown_training_curve.png) |
 140 | 
 141 | ### Agentic RL
 142 | 
 143 | | Task                                                     | Description                                                            | Performance                                                                  |
 144 | | -------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
 145 | | **[General Agent](examples/agent_workflow/)**            | General agentic training with any agentic frameworks                   | [Guide](docs/tutorial/agentic_rl.md)                                         |
 146 | | **[Tau2 Customer Service](examples/tau2/)**              | Customer service agent on Tau2-Bench (retail, airline, telecom)        | [Paper](https://arxiv.org/abs/2601.22607)                                    |
 147 | | **[Search Agent](examples/search_agent/)**               | End-to-end search agent with Tongyi-DeepResearch workflow              | [Training Curve](examples/search_agent/tongyi_deepresearch/reward_curve.png) |
 148 | | **[Tool-Integrated Reasoning](examples/tir/)**           | Multi-turn tool calling during reasoning (Python executor, calculator) | [Training Curve](examples/tir/figures/task_reward.png)                       |
 149 | | **[OpenAI Agents Integration](examples/openai_agents/)** | Integration with OpenAI Agents SDK for agentic workflows               | -                                                                            |
 150 | | **[CAMEL-AI Integration](examples/camel/)**              | Integration with CAMEL-AI framework for agentic RL                     | -                                                                            |
 151 | 
 152 | ### Vision-Language Models
 153 | 
 154 | | Task                                | Description                                               | Performance                                     |
 155 | | ----------------------------------- | --------------------------------------------------------- | ----------------------------------------------- |
 156 | | **[VLM](examples/vlm/)**            | Geometry3K and CLEVR Count 70K visual reasoning with GRPO | -                                               |
 157 | | **[VLM on NPU](examples/vlm_npu/)** | VLM training on Huawei NPU hardware                       | [Benchmark Results](examples/vlm_npu/README.md) |
 158 | 
 159 | ### Alignment & Infrastructure
 160 | 
 161 | | Task                                            | Description                                           | Performance                                       |
 162 | | ----------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------- |
 163 | | **[RLHF Reward Modeling](examples/alignment/)** | Bradley-Terry reward modeling on Anthropic HH-RLHF    | [Training Curve](examples/alignment/rw_curve.png) |
 164 | | **[SkyPilot Deployment](examples/skypilot/)**   | Cloud deployment with SkyPilot (GCP, AWS, Kubernetes) | [Screenshots](examples/skypilot/README.md)        |
 165 | 
 166 | ## 🔧 Support Matrix
 167 | 
 168 | ### 🧠 Algorithms
 169 | 
 170 | All RL algorithms support both asynchronous and synchronous versions by setting
 171 | `max_head_offpolicyness=0`. See [Asynchronous RL Guide](docs/algorithms/async.md).
 172 | 
 173 | | Algorithm                | Documentation                                 | Paper                                          | Configuration                                                     |
 174 | | ------------------------ | --------------------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------- |
 175 | | **GRPO**                 | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/pdf/2402.03300)   | [🔗 GSM8K Example](examples/math/gsm8k_grpo.yaml)                 |
 176 | | **GSPO**                 | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/abs/2507.18071)   | [🔗 GSM8K Example](examples/math/gsm8k_gspo.yaml)                 |
 177 | | **PPO**                  | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/pdf/2203.02155)   | [🔗 GSM8K Example](examples/math/gsm8k_ppo.yaml)                  |
 178 | | **DAPO**                 | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/abs/2503.14476)   | [🔗 GSM8K Example](examples/math/gsm8k_dapo_dynamic_bs.yaml)      |
 179 | | **LitePPO**              | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/abs/2508.08221)   | [🔗 GSM8K Example](examples/math/gsm8k_liteppo.yaml)              |
 180 | | **Dr.GRPO**              | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/abs/2503.20783)   | [🔗 GSM8K Example](examples/math/gsm8k_drgrpo.yaml)               |
 181 | | **REINFORCE++**          | -                                             | [📄 Paper](https://arxiv.org/pdf/2501.03262)   | [🔗 GSM8K Example](examples/math/gsm8k_reinforce.yaml)            |
 182 | | **RLOO**                 | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/pdf/2402.14740v1) | [🔗 GSM8K Example](examples/math/gsm8k_rloo.yaml)                 |
 183 | | **SAPO**                 | [📖 Docs](docs/en/algorithms/grpo_series.md)  | [📄 Paper](https://arxiv.org/abs/2511.20347)   | [🔗 GSM8K Example](examples/math/gsm8k_sapo.yaml)                 |
 184 | | **M2PO**                 | [📖 Docs](docs/algorithms/m2po.md)            | [📄 Paper](https://arxiv.org/abs/2510.01161)   | [🔗 GSM8K Example](examples/math/gsm8k_m2po.yaml)                 |
 185 | | **RLHF Reward Modeling** | -                                             | -                                              | [🔗 RLHF Example](examples/alignment/)                            |
 186 | | **SFT**                  | -                                             | -                                              | [🔗 GSM8K Example](examples/math/gsm8k_sft.py)                    |
 187 | | **Distillation**         | [📖 Docs](docs/en/algorithms/distillation.md) | [📄 Paper](https://arxiv.org/pdf/2506.02208)   | [🔗 GSM8K Example](examples/distillation/gsm8k_grpo_distill.yaml) |
 188 | 
 189 | ### Models
 190 | 
 191 | | Model Family               | Megatron | PyTorch FSDP | PyTorch Archon | Notes                                                    |
 192 | | -------------------------- | -------- | ------------ | -------------- | -------------------------------------------------------- |
 193 | | **Qwen2/3**                | ✅       | ✅           | ✅             | -                                                        |
 194 | | **Qwen3-MoE**              | ✅       | ✅           | ✅             | -                                                        |
 195 | | **Qwen2.5-VL**             | ❌       | ✅           | ❌             | Vision-language model                                    |
 196 | | **Qwen3-VL**               | ❌       | ✅           | ❌             | Vision-language model                                    |
 197 | | **Gemma 3**                | ❌       | ✅           | ❌             | Vision-language model                                    |
 198 | | **Other Hugging Face LLM** | ❌       | ✅           | ❌             | Compatibility depending on the version of `transformers` |
 199 | 
 200 | Check the [AI Coding Assistant Guide](docs/reference/ai_assisted_dev.md) and
 201 | [Archon Reference](docs/tutorial/archon.md) for how to integrate new models into AReaL.
 202 | 
 203 | ### Training Backends
 204 | 
 205 | | Backend            | DP          | Tensor Parallel | Sequence Parallel within TP | Context Parallel | Pipeline Parallel | Expert Parallel | 1D Sequence Packing | LoRA |
 206 | | ------------------ | ----------- | --------------- | --------------------------- | ---------------- | ----------------- | --------------- | ------------------- | ---- |
 207 | | **Megatron**       | ✅ (ZeRO-1) | ✅              | ✅                          | ✅               | ✅                | ✅              | ✅                  | ❌   |
 208 | | **PyTorch FSDP**   | ✅ (FSDP2)  | ✅              | ✅                          | ✅               | ❌                | ❌              | ✅                  | ✅   |
 209 | | **PyTorch Archon** | ✅ (FSDP2)  | ✅              | ✅                          | ✅               | ✅                | ✅              | ✅                  | ❌   |
 210 | 
 211 | ### Inference Backends
 212 | 
 213 | | Backend    | Tensor Parallel | Context Parallel | Pipeline Parallel | Data Parallel Attention | Expert Parallel |
 214 | | ---------- | --------------- | ---------------- | ----------------- | ----------------------- | --------------- |
 215 | | **vLLM**   | ✅              | ❓               | ✅                | ❓                      | ❓              |
 216 | | **SGLang** | ✅              | ❌               | ❌                | ✅                      | ✅              |
 217 | 
 218 | ## 📖 Resources
 219 | 
 220 | ### Tutorial
 221 | 
 222 | - [Installation](docs/en/tutorial/installation.md)
 223 | - [Quickstart](docs/en/tutorial/quickstart.md)
 224 | - [Agentic RL](docs/en/tutorial/agentic_rl.md)
 225 | - [Evaluation](docs/en/tutorial/eval.md)
 226 | - [Large MoE with Megatron](docs/en/tutorial/megatron.md)
 227 | - [Large MoE with PyTorch Archon](docs/en/tutorial/archon.md)
 228 | 
 229 | ### Code Walkthrough
 230 | 
 231 | - [Running GRPO on GSM8K dataset](docs/en/tutorial/gsm8k_grpo.md)
 232 | 
 233 | ### Best Practices
 234 | 
 235 | - [Improving Algorithm Performance](docs/en/best_practices/algo_perf.md)
 236 | - [Agent Workflow Best Practices](docs/en/best_practices/workflow.md)
 237 | - [Debugging](docs/en/best_practices/debugging.md)
 238 | - [Handling OOM Issues](docs/en/best_practices/handling_oom.md)
 239 | - [Performance Profiling](docs/en/best_practices/perf_profiling.md)
 240 | 
 241 | ### Customization
 242 | 
 243 | - [Customize Dataset](docs/en/customization/dataset.md)
 244 | - [Customize Agentic/RVLR Rollout Workflows](docs/en/customization/agent.md)
 245 | 
 246 | ### Algorithms
 247 | 
 248 | - [Asynchronous RL Explained](docs/en/algorithms/async.md)
 249 | - [PPO, GRPO, and Related Algorithms](docs/en/algorithms/grpo_series.md)
 250 | - [M2PO](docs/en/algorithms/m2po.md)
 251 | 
 252 | ### Reference
 253 | 
 254 | - [CLI Configurations](docs/en/cli_reference.md)
 255 | - [Checkpointing](docs/en/reference/checkpointing.md)
 256 | - [Metrics Tracking](docs/en/reference/metrics_tracking.md)
 257 | - [Allocation Mode](docs/en/reference/alloc_mode.md)
 258 | - [Rollout Workflow](docs/en/reference/rollout_workflow.md)
 259 | - [Agent Workflow](docs/en/reference/agent_workflow.md)
 260 | - [AI-Assisted Development](docs/en/reference/ai_assisted_dev.md)
 261 | 
 262 | ## 🤝 Contributing
 263 | 
 264 | We warmly welcome contributions from the community! Whether you're fixing bugs, adding
 265 | features, improving documentation, or helping others, your contribution is valued.
 266 | Please check our **[Contributing Guide](CONTRIBUTING.md)** for detailed information.
 267 | 
 268 | ```bash
 269 | # Fork and clone the repository
 270 | git clone https://github.com/YOUR-USERNAME/AReaL
 271 | cd AReaL
 272 | 
 273 | # Install uv and sync dependencies
 274 | pip install uv
 275 | # Install flash-attn pre-built wheel to avoid compiling from source
 276 | uv pip install "https://github.com/mjun0812/flash-attention-prebuild-wheels/releases/download/v0.7.16/flash_attn-2.8.3+cu128torch2.9-cp312-cp312-linux_x86_64.whl"
 277 | # Use `--extra cuda` on Linux with CUDA (installs training packages + SGLang)
 278 | uv sync --extra cuda --group dev
 279 | # For vLLM instead (note: use torch2.10 flash-attn wheel):
 280 | # uv sync --extra cuda-vllm --group dev
 281 | # Or without CUDA support
 282 | # uv sync --group dev
 283 | 
 284 | # Set up pre-commit hooks (formatting, linting, commit message checks)
 285 | pre-commit install --install-hooks
 286 | 
 287 | # Make changes
 288 | git checkout -b feat/gpt-o5
 289 | git add .
 290 | # `git commit` will automatically check your files and commit messages
 291 | git commit -m "feat: implement gpt-o5 training loop"
 292 | git push
 293 | ```
 294 | 
 295 | ## 🗺️ Future Roadmap
 296 | 
 297 | - **[Full Roadmap](ROADMAP.md)**
 298 | - **[2025 Q4 Roadmap](https://github.com/inclusionAI/AReaL/issues/542)**
 299 | 
 300 | AReaL is under active development with planned minor releases weekly and major releases
 301 | monthly. We warmly welcome community engagement and contributions. We are also
 302 | **actively hiring interns and full-time employees** with open positions in both the US
 303 | and China.
 304 | 
 305 | ## 🙏 Acknowledgments
 306 | 
 307 | We gratefully acknowledge that major contributors are from the AReaL Team at the
 308 | Institute for Interdisciplinary Information Sciences (IIIS), Tsinghua University and Ant
 309 | Group.
 310 | 
 311 | We have also received invaluable assistance from the following groups (listed
 312 | alphabetically):
 313 | 
 314 | - The Data Intelligence Lab at Ant Research for their data support
 315 | 
 316 | - @HwVanICI for support on vLLM, LoRA, NPU integration, and more
 317 | 
 318 | - The [Relaxed System Lab](https://github.com/Relaxed-System-Lab) at HKUST for seamless
 319 |   collaboration on numerous system-related aspects
 320 | 
 321 | - The [SGLang team](https://github.com/sgl-project/sglang) for supporting custom weight
 322 |   update features and their contributions during AReaL-lite development
 323 | 
 324 | - The Super Computing Technology (SCT) team at Ant Group for their expertise in
 325 |   large-scale cluster operations and maintenance
 326 | 
 327 | - Special thanks to @Lyken17 for providing valuable suggestions throughout the API
 328 |   design process
 329 | 
 330 | We also deeply appreciate all pioneering work from the community, particularly the
 331 | [ReaLHF](https://github.com/openpsi-project/ReaLHF) project from OpenPsi Inc. and other
 332 | outstanding projects, including but not limited to
 333 | [DeepScaleR](https://github.com/agentica-project/deepscaler),
 334 | [Open-Reasoner-Zero](https://github.com/Open-Reasoner-Zero/Open-Reasoner-Zero/tree/main),
 335 | [OpenRLHF](https://github.com/OpenRLHF/OpenRLHF),
 336 | [VeRL](https://github.com/volcengine/verl),
 337 | [SGLang](https://github.com/sgl-project/sglang), [QwQ](https://github.com/QwenLM/QwQ),
 338 | [Light-R1](https://github.com/Qihoo360/Light-R1), and
 339 | [DAPO](https://github.com/BytedTsinghua-SIA/DAPO).
 340 | 
 341 | ## 📄 Citation
 342 | 
 343 | ```bibtex
 344 | @inproceedings{mei2025real,
 345 |   author       = {Mei, Zhiyu and Fu, Wei and Li, Kaiwei and Wang, Guangju and Zhang, Huanchen and Wu, Yi},
 346 |   title        = {ReaL: Efficient RLHF Training of Large Language Models with Parameter Reallocation},
 347 |   booktitle    = {Proceedings of the Eighth Conference on Machine Learning and Systems,
 348 |                   MLSys 2025, Santa Clara, CA, USA, May 12-15, 2025},
 349 |   publisher    = {mlsys.org},
 350 |   year         = {2025},
 351 | }
 352 | ```
 353 | 
 354 | ```bibtex
 355 | @misc{fu2025areal,
 356 |       title={AReaL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning},
 357 |       author={Wei Fu and Jiaxuan Gao and Xujie Shen and Chen Zhu and Zhiyu Mei and Chuyi He and Shusheng Xu and Guo Wei and Jun Mei and Jiashu Wang and Tongkai Yang and Binhang Yuan and Yi Wu},
 358 |       year={2025},
 359 |       eprint={2505.24298},
 360 |       archivePrefix={arXiv},
 361 |       primaryClass={cs.LG},
 362 |       url={https://arxiv.org/abs/2505.24298},
 363 | }
 364 | ```
```
