# Missing visibility into failed evaluation rollouts

## Problem

When evaluating model checkpoints, the evaluation pipeline in `src/prime_rl/orchestrator/eval_utils.py` silently discards failed rollouts. The `evaluate_env` function calls `evaluate()` to generate rollouts, but if some rollout groups fail during generation, those failures are dropped without any aggregate tracking. There is no metric recording how many rollouts were requested versus how many succeeded, making it impossible to tell if evaluation results are skewed by missing data.

Specifically:

1. **No failure count metric**: The evaluation metrics logged to the monitor include completion lengths, reward averages, pass@k rates, and truncation stats -- but nothing about how many rollouts failed. If 30% of rollouts fail silently, the reported `avg@k` only reflects the 70% that succeeded, and there's no way to detect this skew.

2. **All-fail case is opaque**: When ALL rollouts fail for an environment, a warning is logged ("All rollouts failed for {env_name}, skipping metrics") but no metrics are reported to the monitoring system at all. This means dashboards show a gap with no explanation -- operators can't distinguish "eval didn't run" from "eval ran but everything failed."

3. **No aggregate failure warning in generation**: In `src/prime_rl/orchestrator/vf_utils.py`, the `generate()` function logs individual group failures but never reports the total count of failed groups. If 5 out of 20 groups fail, you only see 5 individual warnings with no summary.

## Expected behavior

- Track the number of failed rollouts (`total_requested - total_returned`) and include it in evaluation metrics. The metric key must contain the word "fail" (case-insensitive) and should be named `failed_rollouts`. For environment-specific breakdown, use the key format `eval/{env_name}/failed_rollouts` where `{env_name}` is the environment's name.
- When all rollouts fail, still report the failure count to the monitoring system via `monitor.log()` so dashboards reflect what happened.
- After generation completes, log an aggregate summary warning that mentions both the number of failed groups and the total group count, in the form `"N/M groups failed"` (e.g., "2/5 groups failed"). The summary warning must be distinct from individual group failure messages and should not contain the exact string "Group failed:".

## Files to investigate

- `src/prime_rl/orchestrator/eval_utils.py` -- `evaluate_env()` function
- `src/prime_rl/orchestrator/vf_utils.py` -- `generate()` and `evaluate()` functions

## Metrics schema

When logging metrics via `monitor.log()`, include at minimum:
- A key containing "fail" (case-insensitive) with an integer value equal to the number of failed rollouts (requested - returned)
- Optionally, a key in the format `eval/{env_name}/failed_rollouts` with the same value
- Standard keys: `progress/ckpt_step` and `step` (if the monitoring API requires them)
