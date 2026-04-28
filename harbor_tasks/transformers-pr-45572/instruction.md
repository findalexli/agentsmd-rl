# Fix Dots1MoE Expert Routing Masked Fill Value

## Problem

In the `Dots1MoE` model, the `route_tokens_to_experts` method incorrectly fills
masked (excluded) expert positions with the value `0.0` using
`torch.Tensor.masked_fill`.  When expert selection scores happen to be negative
— which can occur due to per-expert correction biases stored in
`e_score_correction_bias` — the masked positions scored at `0.0` outrank the
valid-but-negative expert scores.  This causes `torch.topk` to select excluded
experts, routing tokens to the wrong experts.

The parent class `DeepseekV3MoE` already handles this correctly — compare its
`route_tokens_to_experts` implementation to identify the difference.

## Expected Behavior

When valid expert scores are negative (e.g., due to sufficiently negative
`e_score_correction_bias` values), the `topk` selection must pick from the
valid experts only, never from the masked-out group. Masked positions must
not outrank valid negative scores.

## Context

Transformers uses a "modular" system for code generation: model definitions
live in `modular_<name>.py` files, and the standalone `modeling_<name>.py`
files are generated from them via `make fixup`. The Dots1 model uses this
modular system, with `Dots1MoE` inheriting from `DeepseekV3MoE`.

## Requirements

- The fix must be durable against `make fixup` regenerating generated files.
- Keep the change minimal — this is a bugfix, not a refactor.

## Code Style Requirements

Run `make fixup` after making changes to ensure the modular and modeling files
are consistent.
