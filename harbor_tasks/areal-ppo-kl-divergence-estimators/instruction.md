# Add KL Divergence Estimators to PPO Actor Stats

## Context

AReaL's PPO actor (`areal/trainer/ppo/actor.py`) tracks various training diagnostics
via `stats_tracker` — proximal policy approximation metrics, version staleness, etc.

One important missing diagnostic is **KL divergence estimation** between the
inference-time policy and the training-time policy. When running "true on-policy" RL
(where the rollout policy and training policy may drift), monitoring KL divergence
helps detect and quantify policy drift.

## Problem

The function `_log_proximal_approximation_stats` in `areal/trainer/ppo/actor.py`
already has access to both `logprobs` (current/training-time policy log-probabilities)
and `old_logp` (behavior/inference-time policy log-probabilities), but it does not
compute or log any KL divergence estimators between them.

Three standard estimators should be tracked:

1. **Direct estimator**: the simplest first-order estimator
2. **Taylor (second-order) estimator**: a quadratic approximation
3. **Dual estimator**: based on the convex conjugate / Donsker-Varadhan bound

All three are functions of the log-ratio between the two policies. They should be
logged under the existing `stats_tracker` scope used by this function, using
`denominator="n_valid_tokens"` for proper per-token averaging.

## Requirements

- Add the KL divergence estimators inside `_log_proximal_approximation_stats`
- Only compute when `logprobs` is available (not None)
- Use `.float()` and `.detach()` appropriately (follow existing patterns in the function)
- Register all three estimators with `stats_tracker.stat()`
- The computation should be within the existing `stats_tracker.scope("compute_logp")` block

## References

- See the existing stats logging patterns in `_log_proximal_approximation_stats`
- The `stats_tracker` API: `stats_tracker.stat(name=tensor, denominator="key")`
