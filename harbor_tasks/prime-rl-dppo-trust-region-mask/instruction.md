# Update Default Loss to DPPO+KL

## Problem

The default trust region mask in `default_loss_fn` (`src/prime_rl/trainer/rl/loss.py`) masks tokens unconditionally in both directions -- both high-side (probability increased too much) and low-side (probability decreased too much) violations are masked regardless of whether the advantage is positive or negative.

Based on ablation results, this should use DPPO-style advantage-conditioned masking: for tokens with positive advantage, only mask high-side violations (upweight trust region); for tokens with negative advantage, only mask low-side violations (downweight trust region).

Additionally, the config fields and internal variable names use the outdated `ipo_` prefix and should be renamed to `dppo_` to reflect the algorithm. This is a breaking config change.

## Expected Behavior

- Trust region mask is conditioned on advantage sign
- Config fields use `dppo_mask_low` / `dppo_mask_high` instead of `ipo_mask_low` / `ipo_mask_high`
- Masking metrics (`is_masked_high`, `is_masked_low`) reflect advantage-conditioned gating
- Unit tests updated to use new field names

## Files to Look At

- `src/prime_rl/trainer/rl/loss.py` -- `default_loss_fn` with the masking logic
- `src/prime_rl/configs/trainer.py` -- `DefaultLossConfig` with threshold fields
- `tests/unit/train/rl/test_loss.py` -- tests referencing config fields
