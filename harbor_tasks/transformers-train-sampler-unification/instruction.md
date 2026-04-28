# Train Sampler Unification

## Problem

The `transformers` library's training pipeline currently uses a boolean flag called `group_by_length` to control whether training uses random sampling or length-grouped sampling. This design has several limitations:

1. Only two sampling modes exist: the default random behavior and `group_by_length`
2. Users have requested a `"sequential"` sampling mode for deterministic, reproducible training runs
3. Adding more boolean flags for each new sampling strategy does not scale

## Desired Behavior

The training configuration should expose a unified string parameter named `train_sampling_strategy` that can be set to one of three values:

- `"random"` — uses the default random sampler (equivalent to current default behavior)
- `"sequential"` — uses a `SequentialSampler` for deterministic epoch ordering
- `"group_by_length"` — uses the existing `LengthGroupedSampler` (equivalent to current `--group_by_length` behavior)

The old `group_by_length` boolean parameter should no longer exist. The `train_sampling_strategy` parameter must default to `"random"` and its set of valid values should be documented via the dataclass field's `metadata` dictionary under the `"choices"` key, following existing patterns in the codebase.

## Sampling Logic

The method that builds the training sampler (`_get_train_sampler`) must be updated to inspect the new parameter name rather than the old boolean flag. It should return:

- `SequentialSampler` when the strategy is `"sequential"`
- `LengthGroupedSampler` when the strategy is `"group_by_length"`
- `RandomSampler` otherwise (the default)

The evaluation sampler method (`_get_eval_sampler`) also references this configuration option and must be updated accordingly.

## IterableDataset Handling

When training uses an `IterableDataset`, samplers cannot be used because they require indexed access. Currently, using a non-default sampling option with an `IterableDataset` causes the training script to crash with a `ValueError` during argument validation in `_validate_args`. Instead of crashing, the code should call `logger.info(` to emit an info-level message noting that the `train_sampling_strategy` argument is ignored for `IterableDataset`. Training should proceed normally after logging.

## Example Commands

The speech recognition examples directory contains a README with 6 training command examples that pass `--group_by_length` as a command-line flag. These example commands must be updated to use `--train_sampling_strategy group_by_length` instead, which is the new CLI argument format that maps to the unified parameter.

## Verification

After the changes:
1. The configuration class should accept initialization with `train_sampling_strategy` set to any of the three valid values without error
2. The example commands in the README should all use `--train_sampling_strategy group_by_length` and no command should use the old `--group_by_length` flag
3. The module should import successfully
4. Using any sampling strategy with an `IterableDataset` should not crash the training script
