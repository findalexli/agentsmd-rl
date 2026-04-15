# Add Checkpoint Resume Functionality

## Problem

The training system lacks checkpoint resume functionality. Users cannot:
- Resume training from a previously saved checkpoint
- Configure checkpoint intervals and paths
- Understand the relationship between checkpoints and weight files

The codebase currently uses a mix of checkpoint naming conventions (some files reference `model.pt` while others may need to use `pytorch_model.bin`). The README documentation also needs restructuring: the "## Contributing" section should be renamed to "## Developer" and "### Config System" should become "### Configs".

## Requirements

### 1. Checkpoint Manager Implementation

Implement checkpoint management for the training system:
- **Trainer CheckpointManager**: A class in `src/zeroband/training/ckpt.py` with `save()` and `load()` methods for persisting and restoring training progress
- **Orchestrator CheckpointManager**: A class in `src/zeroband/training/orchestrator/ckpt.py` with `save()` and `load()` methods for distributed training coordination
- **Progress State Tracking**: The checkpoint system must track `step` (incremented on save), `epoch`, `total_tokens`, and `total_samples`

### 2. Checkpoint Configuration

Update the training configuration to support:
- `resume_step` field (integer, minimum value 1) for specifying which step to resume from
- `save_async` field for controlling asynchronous checkpoint saves
- Checkpoint path configuration for specifying where checkpoints are stored
- Interval configuration for controlling how frequently checkpoints are saved

### 3. Weight Checkpointing Module

Create `src/zeroband/training/weights.py` that:
- Provides a `save_weight_checkpoint` function
- Saves model weights as `pytorch_model.bin` (HuggingFace format)

### 4. Orchestrator Configuration Updates

Update the orchestrator configuration:
- Replace any `PathConfig` nested structure with direct `Path` fields named `rollout_path` and `weights_path`
- Add a `clean` boolean flag for controlling cleanup behavior
- Update `src/zeroband/training/orchestrator/utils.py` to reference `pytorch_model.bin` instead of `model.pt`
- Update `src/zeroband/training/orchestrator/client.py` to reference `pytorch_model.bin`

### 5. Documentation Updates

Update `README.md` with:
- A new "### Checkpointing" subsection explaining:
  - How to resume training with `--ckpt.resume_step` CLI flag
  - The step directory structure (checkpoint directories named `step_{n}`)
  - The relationship between checkpoints and weight files
  - Configuration options for checkpoint paths, intervals, and async saving
- Rename "## Contributing" to "## Developer"
- Rename "### Config System" to "### Configs"

### 6. Existing Test Compatibility

The following existing tests must continue to pass:
- `tests/unit/training/test_config.py`
- `tests/unit/training/test_env.py`
- `tests/unit/training/test_logger.py`
- `tests/unit/training/test_world.py`
- `tests/unit/training/orchestrator/test_config.py`
- `tests/unit/eval/test_config.py`
- `tests/unit/inference/test_config.py`

### 7. Project Integrity Requirements

- `pyproject.toml` must remain valid TOML with `[project]` and `dependencies` sections
- All TOML files in `configs/` directory must remain valid
- All Python files must have valid syntax and be importable
- Ruff linting must pass with flags: `--select F,I --ignore F722,F821`

## Files to Look At

- `README.md` - main documentation file to update
- `src/zeroband/training/` - training code directory
- `src/zeroband/training/orchestrator/` - orchestrator code directory
- `pyproject.toml` - project configuration
- `configs/` - configuration files
