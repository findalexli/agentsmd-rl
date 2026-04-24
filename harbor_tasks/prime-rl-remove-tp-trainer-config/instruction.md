# Remove unsupported tensor parallelism option from trainer

The trainer's `ModelConfig` class defines a `tp` (tensor parallelism) configuration field that defaults to 1. However, tensor parallelism is not actually supported by the trainer and there are no plans to support it. This dead configuration field inflates parallelism calculations in multiple places, causing `non_data_parallel_size` and `seq_len_divisor` to return higher values than they should.

## Observed symptoms

- `non_data_parallel_size` returns `cp * tp * pp` when it should return `cp * pp`
- `seq_len_divisor` returns `tp * cp * 2` when it should return `cp * 2`
- Any code that multiplies by `model.tp` when computing parallelism is using dead code

## Required changes

1. **Remove the `tp` field from `ModelConfig`** entirely — configs that include `tp` should be rejected
2. **Remove `tp` from `ParallelDims`** — the field, `tp_enabled` property, and all TP-related math in `non_data_parallel_size`, `seq_len_divisor`, and mesh dimension validation
3. **Update downstream calculations** — any code that multiplies by `model.tp` for worker counts, micro-batch sizing, dataset sharding, or token accounting should be updated to remove those multiplications
4. **Document the breaking change** in `CHANGELOG.md` so users know to remove `tp` from their configs

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
