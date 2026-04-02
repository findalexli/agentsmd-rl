# Validation dataloader uses wrong sampler, causing biased evaluation metrics

## Bug Description

The `create_dataloader` function in `areal/utils/dataloader.py` currently uses `DistributedSampler` for **all** dataset types, including validation datasets. This causes two problems during distributed evaluation:

1. **Padding**: `DistributedSampler` pads the dataset to make it evenly divisible across replicas. For validation, this means some samples are evaluated **twice**, inflating metrics.
2. **Dropping**: The sampler's `drop_last` is hardcoded to `True`, which truncates the last incomplete batch of validation samples.

Combined, these issues mean validation metrics are computed on a distorted view of the data — some samples counted twice (padding) and others dropped entirely.

## Expected Behavior

For **validation** dataloaders (i.e., when the config is a validation dataset config), the sampler should:
- **Not pad** the dataset — every sample should be evaluated exactly once across all replicas, even if ranks end up with slightly different numbers of samples.
- **Not drop the last batch** — the sampler should use `drop_last=False`.

Training dataloaders should continue to use the standard `DistributedSampler` with `drop_last=True` as before.

## Relevant Files

- `areal/utils/dataloader.py` — the `create_dataloader` function
- `areal/api/cli_args.py` — defines `_DatasetConfig`, `TrainDatasetConfig`, and `ValidDatasetConfig`

## Reproduction

Create a dataset with a size not evenly divisible by the number of replicas (e.g., 10 samples with 3 replicas). Use `create_dataloader` with a validation config and observe:
- The total number of indices across all ranks exceeds the dataset size (padding)
- Some indices appear more than once
