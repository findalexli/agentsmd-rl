# Update Default Loss to DPPO+KL

## Problem

The default trust region mask in `default_loss_fn` masks tokens whenever the probability difference exceeds a threshold, without considering the sign of the advantage. Tokens are masked for both "high-side" (probability increased too much) and "low-side" (probability decreased too much) violations regardless of whether the advantage is positive or negative.

This unconditional masking causes valid tokens to be incorrectly excluded. For example, a token with positive advantage that has its probability increased (a "high-side" violation) should be allowed through, not masked.

## Expected Behavior

- Trust region masking is gated by advantage sign: positive advantages only gate high-side violations, negative advantages only gate low-side violations
- Config field names use the DPPO-style prefix. Specifically, `DefaultLossConfig` must have fields named `dppo_mask_low` and `dppo_mask_high`. The old IPO-style field names (`ipo_mask_low`, `ipo_mask_high`) must no longer exist.
- Metrics exposed by the loss function correctly reflect which tokens were masked and why (tracked via `is_masked` metric)