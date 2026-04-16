# Train Sampler Unification

## Problem

The `transformers` library currently has a `group_by_length` boolean parameter in `TrainingArguments` that controls whether to use the `LengthGroupedSampler` during training. This is limiting because:

1. We only have two options: random sampling (default) or group_by_length
2. Users have requested sequential sampling for deterministic/reproducible training
3. The API is not extensible for future sampling strategies

## Requirements

Refactor the training sampler selection to use a unified `train_sampling_strategy` parameter instead of the boolean `group_by_length` flag. The implementation must satisfy these requirements:

### Parameter Specification
- Replace `group_by_length: bool` with `train_sampling_strategy: str` in `TrainingArguments`
- Default value must be `"random"`
- Must accept exactly three values: `"random"`, `"sequential"`, and `"group_by_length"`

### Behavior Requirements
1. **Random sampling** (`"random"`): Use PyTorch's `RandomSampler` for training (this is the current default behavior)
2. **Sequential sampling** (`"sequential"`): Use PyTorch's `SequentialSampler` for deterministic iteration order
3. **Group by length** (`"group_by_length"`): Use the existing `LengthGroupedSampler` for bucketing similar-length sequences

### IterableDataset Handling
When training with an `IterableDataset`, the sampling strategy selection should be ignored gracefully. Instead of raising a `ValueError`, the code should log an info message of the form: `The `train_sampling_strategy={value}` argument is ignored when using an IterableDataset.`

### Documentation Updates
The `examples/pytorch/speech-recognition/README.md` contains 6 example commands that currently use `--group_by_length`. All 6 examples must be updated to use the new parameter format `--train_sampling_strategy group_by_length` instead.

## Files to Modify

- `src/transformers/training_args.py` - Define the new parameter with its default and valid choices
- `src/transformers/trainer.py` - Implement the sampler selection logic based on the new parameter
- `examples/pytorch/speech-recognition/README.md` - Update all 6 example commands

## Verification

After making changes:
1. `TrainingArguments` should accept all three sampling strategies: `"random"`, `"sequential"`, `"group_by_length"`
2. The README examples should use `--train_sampling_strategy group_by_length` format
3. The transformers module should import without errors
4. When using `IterableDataset`, an info message should be logged instead of raising an exception
