# Update Default Loss to DPPO+KL

## Problem

The default trust region mask in `default_loss_fn` (`src/prime_rl/trainer/rl/loss.py`) masks tokens whenever the probability difference exceeds a threshold, without considering the sign of the advantage. Tokens are masked for both "high-side" (probability increased too much) and "low-side" (probability decreased too much) violations regardless of whether the advantage is positive or negative.

This unconditional masking causes valid tokens to be incorrectly excluded. For example, a token with positive advantage that has its probability increased (a "high-side" violation) should be allowed through, not masked.

## Expected Behavior

- Trust region masking is gated by advantage sign: positive advantages only gate high-side violations, negative advantages only gate low-side violations
- Config field names reflect the current algorithm (DPPO-style), not the previous algorithm prefix
- Metrics exposed by the loss function correctly reflect which tokens were masked and why

## Files to Look At

- `src/prime_rl/trainer/rl/loss.py` — `default_loss_fn` with the masking logic
- `src/prime_rl/configs/trainer.py` — `DefaultLossConfig` with threshold fields
- `tests/unit/train/rl/test_loss.py` — tests referencing config fields

## Constraints

- The fix must preserve backward compatibility for any other callers of `default_loss_fn` that use the current config field names
- All existing unit tests must pass with their current import patterns