# Add KL Divergence Estimators to PPO Actor Stats

## Context

AReaL's PPO actor tracks various training diagnostics via `stats_tracker` — proximal
policy approximation metrics, version staleness, etc. One important missing diagnostic is
**KL divergence estimation** between the inference-time policy and the training-time
policy. When running "true on-policy" RL (where the rollout policy and training policy
may drift), monitoring KL divergence helps detect and quantify policy drift.

## Problem

The function that handles `logprobs` and `old_logp` tracking has access to both
policy log-probabilities but does not compute or log any KL divergence estimators
between them.

The `log_ratio = logprobs.float() - old_logp.float()` is the fundamental quantity.
Three standard estimators should be computed from this:

1. **Direct estimator**: `direct = -log_ratio`
2. **Taylor (second-order) estimator**: `taylor = log_ratio² / 2`
3. **Dual estimator**: `dual = exp(log_ratio) - 1 - log_ratio`

All three should be registered with `stats_tracker.stat()` using
`denominator="n_valid_tokens"` for proper per-token averaging.

## Requirements

- Only compute the KL estimators when `logprobs` is available (not None)
- Use `.detach()` on tensors to prevent gradient tracking (the log_ratio itself
  should be detached before computing estimators)
- Register all three estimators with `stats_tracker.stat()`, e.g.:
  `stats_tracker.stat(kl_div_direct=..., kl_div_taylor=..., kl_div_dual=..., denominator="n_valid_tokens")`
- Follow the existing patterns for float conversion and detachment used by other
  stats in the same function

## Verification

The implemented estimators can be verified against these expected values for
`logprobs=[-1.0, -2.0, -3.0]` and `old_logp=[-1.5, -2.5, -3.5]`:
- direct should equal `[-0.5, -0.5, -0.5]`
- taylor should equal `[0.125, 0.125, 0.125]`
- dual should be non-negative for all valid inputs

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
