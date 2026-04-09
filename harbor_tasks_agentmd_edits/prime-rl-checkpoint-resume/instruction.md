# Implement Checkpoint Resume for RL Training

## Problem

The current training system lacks the ability to resume training from a saved checkpoint. When training is interrupted (e.g., due to hardware failure or preemption), users must start from scratch. The codebase needs:

1. A `CheckpointManager` abstraction for both the trainer and orchestrator that can save/load progress
2. Support for resuming training from a specific step via `--ckpt.resume_step`
3. The orchestrator needs its own checkpointing mechanism to track progress (step, epoch, tokens, samples, problems)
4. The weight checkpoint file format should use `pytorch_model.bin` (standard HF format) instead of `model.pt`
5. The orchestrator config structure needs to be simplified (replace `PathConfig` with direct `Path` fields)

## Expected Behavior

After implementing this feature:

1. **Trainer CheckpointManager** (`src/zeroband/training/ckpt.py`): A class with `save()` and `load()` methods that saves FSDP model shard, optimizer state, and training progress (step, total_tokens, total_samples) to `{ckpt.path}/step_{step}/trainer.pt`

2. **Orchestrator CheckpointManager** (`src/zeroband/training/orchestrator/ckpt.py`): A new class with `save()` and `load()` methods that saves orchestrator progress to `{ckpt.path}/step_{step}/orchestrator.pt`

3. **Weight Checkpoint Module** (`src/zeroband/training/weights.py`): Move `save_weight_checkpoint` here, update to save as `pytorch_model.bin`

4. **Config Changes**:
   - `CheckpointConfig` should have `resume_step` (int, ge=1) instead of `resume_path`
   - `CheckpointConfig` should have `save_async` bool field
   - Orchestrator config: replace `rollout` (PathConfig) with `rollout_path` (Path), `weights` with `weights_path`, add `clean` bool

5. **Orchestrator Integration** (`src/zeroband/training/orchestrator/orchestrator.py`): Use `progress.step` instead of loop variable, load checkpoint on resume, save checkpoint at intervals

6. **Trainer Integration** (`src/zeroband/training/train.py`): Initialize `CheckpointManager`, load checkpoint if `resume_step` set, save checkpoints at intervals

7. **Update References**: Change `model.pt` to `pytorch_model.bin` in `utils.py` and `client.py`

8. **Documentation** (`README.md`): Add a "Checkpointing" section explaining:
   - How to save checkpoints (`--ckpt.interval`)
   - How to resume (`--ckpt.resume_step`)
   - Directory structure (`checkpoints/step_{n}/`)
   - The relationship between checkpoints and weight files

## Files to Look At

- `src/zeroband/training/ckpt.py` — Refactor to CheckpointManager class
- `src/zeroband/training/config.py` — Add resume_step, save_async fields
- `src/zeroband/training/train.py` — Integrate checkpoint resume
- `src/zeroband/training/orchestrator/ckpt.py` — Create new orchestrator checkpoint module
- `src/zeroband/training/orchestrator/config.py` — Update config structure
- `src/zeroband/training/orchestrator/orchestrator.py` — Integrate orchestrator checkpointing
- `src/zeroband/training/orchestrator/client.py` — Update weight file reference
- `src/zeroband/training/orchestrator/utils.py` — Update weight file reference
- `src/zeroband/training/weights.py` — Create new weight checkpoint module
- `README.md` — Document the checkpointing feature

## Key Design Notes

- The checkpoint manager should increment progress.step when saving (so checkpoint at step N contains progress for step N+1)
- The orchestrator uses a `while` loop with `progress.step` instead of `for step in range()`
- When resuming, the orchestrator needs to reload weights from the appropriate step considering `async_level`
- The weight cleanup logic needs to preserve checkpoints in the range `[x-async_level, x]` for resuming
