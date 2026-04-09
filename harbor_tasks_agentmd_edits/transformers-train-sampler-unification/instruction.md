# Unify train sampling strategy in Trainer

## Problem

The `Trainer` class currently uses a boolean `group_by_length` parameter in `TrainingArguments` to control whether samples are grouped by length during training. This is limiting because:

1. There's no way to use sequential sampling (useful for debugging and reproducibility)
2. The sampling strategy isn't extensible — adding new strategies requires adding more boolean flags
3. Using `group_by_length=True` with an `IterableDataset` raises a hard `ValueError` instead of gracefully handling the incompatibility

## Expected Behavior

Replace the boolean `group_by_length` field with a unified `train_sampling_strategy` string parameter that accepts:
- `"random"` (default, replacing the old `group_by_length=False` behavior)
- `"sequential"` (new — uses `SequentialSampler`)
- `"group_by_length"` (replaces `group_by_length=True`)

The `Trainer` should use this new parameter in both `_get_train_sampler` and `_get_eval_sampler`. When an `IterableDataset` is used, it should log an informational message rather than raising an error.

## Files to Look At

- `src/transformers/training_args.py` — defines the `TrainingArguments` dataclass fields and their documentation
- `src/transformers/trainer.py` — implements sampler selection in `_get_train_sampler` and `_get_eval_sampler`, and validates args in `_validate_args`

After making the code changes, update the relevant documentation files that reference the old `group_by_length` parameter to use the new `train_sampling_strategy` parameter instead. This includes ASR tutorial docs and the speech recognition examples README.
