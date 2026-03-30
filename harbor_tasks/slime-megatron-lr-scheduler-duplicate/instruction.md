# Fix duplicate Megatron LR scheduler resume when optimizer state is not loaded

## Problem

When resuming training from a checkpoint with `--no-load-optim` (to load model weights but skip optimizer/scheduler state), the learning rate scheduler is incorrectly fast-forwarded to the checkpoint iteration. This causes the LR to be pushed directly to `min_lr` at startup, resulting in an observed `lr = 0` behavior.

The root cause is in `slime/backends/megatron_utils/model.py` in the `initialize_model_and_optimizer()` function. After `load_checkpoint()` is called (which already restores the scheduler state via `opt_param_scheduler.load_state_dict(...)` when optimizer state is being resumed), there is an additional manual call to `opt_param_scheduler.step(increment=iteration * args.global_batch_size)`. This call is:

1. **Redundant** when optimizer state IS loaded: Megatron already restores the scheduler state inside `load_checkpoint()`.
2. **Harmful** when optimizer state is NOT loaded (`--no-load-optim`): The fresh scheduler is fast-forwarded to the checkpoint iteration, pushing the LR to `min_lr` immediately.

## Expected Behavior

When `--no-load-optim` is used, the scheduler should start fresh (as intended), and the learning rate should begin at the configured initial value rather than jumping to `min_lr`.

When optimizer state IS loaded, the scheduler state should be restored only by `load_checkpoint()` without any additional fast-forwarding.

## File to Modify

- `slime/backends/megatron_utils/model.py` -- the `initialize_model_and_optimizer()` function
