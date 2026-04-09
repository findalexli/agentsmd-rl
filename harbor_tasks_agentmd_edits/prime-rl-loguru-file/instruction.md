# Update Loguru File Extensions and Documentation

## Problem

The logging system in `prime-rl` has inconsistent file extensions and needs documentation updates to match the new workflow.

### Code Issues

1. **Log file extension inconsistency**: Logger files in `src/prime_rl/rl.py`, `src/prime_rl/trainer/logger.py`, and `src/prime_rl/orchestrator/logger.py` use `.log` extension but should use `.loguru` to properly identify loguru-generated logs.

2. **Bug in log cleaning glob pattern**: In `src/prime_rl/rl.py`, the log cleaning code uses a glob pattern `*.log|*.stdout` which appears to be incorrect - it should likely match `.log` and `.loguru` files instead.

3. **Tail process not tracked**: The `tail -F logs/trainer.log` process started in `src/prime_rl/rl.py` is not added to the `processes` list, meaning it won't be properly cleaned up on shutdown.

### Documentation Issue

The README.md needs to be updated to reflect the new recommended workflow:
- The `tmuxinator` workflow has been reorganized with a "Trainer" pane as the primary entry point
- A new "Standalone Inference Server" section should document how to run the inference server separately to avoid vLLM warmup overhead
- The tmuxinator layout in `.tmuxinator.yaml` needs to match the documented workflow

## Files to Look At

- `src/prime_rl/rl.py` — Main RL entrypoint with logger setup, log cleaning, and process management
- `src/prime_rl/trainer/logger.py` — Trainer logger setup
- `src/prime_rl/orchestrator/logger.py` — Orchestrator logger setup
- `README.md` — Documentation for the RL workflow and tmuxinator setup
- `.tmuxinator.yaml` — Tmux layout configuration

## Expected Changes

1. Update all logger file extensions from `.log` to `.loguru`
2. Fix the log cleaning glob pattern to properly match log files
3. Track the tail process in the processes list for proper cleanup
4. Update README.md to document the new tmuxinator workflow and standalone inference server
5. Update `.tmuxinator.yaml` to match the documented pane structure
