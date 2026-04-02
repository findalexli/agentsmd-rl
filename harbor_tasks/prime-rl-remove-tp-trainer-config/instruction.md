# Remove unsupported tensor parallelism option from trainer

The trainer's `ModelConfig` in `src/prime_rl/configs/trainer.py` defines a `tp` (tensor parallelism) configuration field, but tensor parallelism is not actually supported by the trainer and there are no plans to support it. This dead configuration option is wired through multiple files, inflating parallelism calculations and confusing developers who might try to use it.

## Problem

The `tp` field in `ModelConfig` defaults to 1 but leaks into:

1. **`src/prime_rl/trainer/parallel_dims.py`** — `ParallelDims` includes `tp` in its mesh construction, dimension validation math, `non_data_parallel_size`, and `seq_len_divisor` calculations. The `tp_enabled` property and all TP-related logic are dead code.

2. **`src/prime_rl/configs/rl.py`** — `auto_setup_deployment` multiplies by `tp` when computing `non_data_parallel_size` for worker count.

3. **`src/prime_rl/trainer/sft/train.py`** — SFT training multiplies by `model.tp` in micro-batch sizing, dataset sharding, token accounting, and sequence-length divisibility checks, all unnecessarily.

## Expected outcome

- Remove the `tp` field from `ModelConfig` entirely so configs that include it are rejected
- Remove all TP references from `ParallelDims` (field, validation, mesh dimensions, properties)
- Update all downstream calculations in RL config and SFT training to no longer factor in TP
- Document the breaking change in `CHANGELOG.md`
