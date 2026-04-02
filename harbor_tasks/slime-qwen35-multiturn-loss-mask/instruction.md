# Qwen3.5 multi-turn SFT loss masking is broken

## Bug description

When running supervised fine-tuning (SFT) with a Qwen3.5 model, the loss masking system does not support Qwen3.5's chat template format. The `--loss-mask-type` argument in `slime/utils/arguments.py` only accepts `qwen`, `qwen3`, and `distill_qwen`.

Using the default `qwen` loss-mask type with Qwen3.5 multi-turn messages crashes with:

```
jinja2.exceptions.TemplateError: No user query found in messages.
```

Using `--loss-mask-type qwen3` avoids the crash but produces incorrect loss masks for multi-turn conversations. Specifically, the `qwen3` path processes each assistant turn in isolation, which causes it to reconstruct extra `<think>` reasoning content for historical assistant turns. For Qwen3.5, historical assistant turns should keep only the final answer, not the full reasoning chain. This leads to supervising unnecessary thinking tokens, increasing training cost and producing incorrect gradient signals.

Additionally, the `MultiTurnLossMaskGenerator` constructor in `slime/utils/mask_utils.py` unconditionally calls `get_system_message_length()` during initialization regardless of the tokenizer type, which can fail or produce wrong results for tokenizers that don't follow the qwen/qwen3 chat template structure.

The SFT rollout code in `slime/rollout/sft_rollout.py` also lacks a defensive check to verify that the `token_ids` and `loss_mask` returned by the mask generator have the same length, which could lead to silent training corruption.

## Relevant files

- `slime/utils/mask_utils.py` — `MultiTurnLossMaskGenerator` class, `get_loss_mask()` method
- `slime/utils/arguments.py` — `--loss-mask-type` argument definition (search for `loss-mask-type`)
- `slime/rollout/sft_rollout.py` — `generate_rollout()` function that calls `get_loss_mask()`

## Expected behavior

1. A dedicated Qwen3.5 loss mask type should be available and correctly handle Qwen3.5 multi-turn chat template rendering
2. The mask generator should derive token-level supervision from the fully rendered conversation text, not by processing each turn in isolation
3. For historical assistant turns, only the final answer should be supervised (not reconstructed reasoning tokens)
4. The `<think>` block prefix in assistant turns should be excluded from supervision
5. The constructor should only call `get_system_message_length()` for tokenizer types that need it
6. The SFT rollout should validate that `token_ids` and `loss_mask` lengths match
