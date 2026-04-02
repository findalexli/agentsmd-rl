# Missing Option to Skip Optimizer State When Resuming from Checkpoint

## Problem

When resuming training from a checkpoint, the `CheckpointConfig` class (in `src/prime_rl/configs/trainer.py`) provides several flags to selectively skip loading parts of the saved state:

- `skip_progress` — skip loading the training progress
- `skip_scheduler` — skip loading the learning rate scheduler
- `skip_dataloader` — skip loading the dataloader state

However, there is no option to skip loading the **optimizer state**. This is a real gap: when you want to resume from a checkpoint with model weights but restart optimization from scratch (e.g., after changing the optimizer config, switching from one optimizer to another, or fine-tuning with a fresh optimizer), you are forced to load the full optimizer state anyway.

The checkpoint loading logic lives in `CheckpointManager.load_from_path()` in `src/prime_rl/trainer/ckpt.py`. Currently it always passes the full list of optimizers to `AppState`, which means `dcp_load` always attempts to restore their state from the checkpoint.

## Expected Behavior

There should be a configuration flag in `CheckpointConfig` that, when enabled, causes the checkpoint loader to skip restoring optimizer states. The model weights should still be loaded normally — only the optimizer state should be omitted, effectively restarting optimization while preserving the model.

## Affected Files

- `src/prime_rl/configs/trainer.py` — `CheckpointConfig` class (where `skip_progress`, `skip_scheduler`, etc. are defined)
- `src/prime_rl/trainer/ckpt.py` — `CheckpointManager` class, specifically the `load_from_path` method
