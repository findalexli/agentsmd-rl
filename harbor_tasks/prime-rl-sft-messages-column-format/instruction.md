# SFT Trainer: Support raw `messages` column in datasets

## Problem

The SFT trainer's `SFTDataset` class in `src/prime_rl/trainer/sft/data.py` only accepts datasets structured with separate `prompt` and `completion` columns. This is limiting for users who have datasets in the common "messages" format — a single column containing the full conversation as a list of message dicts (e.g., `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`).

When a dataset with a `messages` column is passed to the SFT trainer, it raises a `ValueError` requiring `prompt` and `completion` columns, even though the codebase already has utility functions in `src/prime_rl/utils/chat_template.py` that could handle message normalization.

## Expected Behavior

1. When a dataset row has a `messages` column, the trainer should interpret it as a complete conversation and process it for training (applying the same tokenization, tool call deserialization, content stripping, and loss masking as the existing prompt/completion path).
2. When both `messages` and `prompt`/`completion` are present in the same row, `messages` should take precedence.
3. The error message when neither format is present should inform users about both supported formats.

## Relevant Files

- `src/prime_rl/trainer/sft/data.py` — `SFTDataset._process()` method
- `src/prime_rl/utils/chat_template.py` — existing message normalization utilities
- `tests/unit/train/sft/test_sft_dataset.py` — existing tests
- `docs/entrypoints.md` — documentation about supported dataset formats
