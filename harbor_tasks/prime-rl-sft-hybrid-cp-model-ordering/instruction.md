# Bug: SFT trainer crashes during context-parallel initialization

## Summary

The SFT trainer in `src/prime_rl/trainer/sft/train.py` crashes with a `NameError` when context parallelism (CP) is enabled. The hybrid CP setup step references the model object before it has been constructed.

## Reproduction

Run the SFT trainer with context parallelism enabled (e.g., `cp > 1` in the config). The trainer will crash during initialization before training begins.

## Relevant code

Look at the `train()` function in `src/prime_rl/trainer/sft/train.py`. The function:

1. Sets up parallel dimensions and CP groups (around line 100-110)
2. Sets up checkpoint managers
3. Initializes the model via `setup_model()`

The hybrid CP configuration step that configures DeltaNet/linear-attention modules for models like Qwen3.5 MoE is called at the wrong point in the initialization sequence. It needs the actual model instance to operate on, but the model hasn't been created yet when it runs.

## Expected behavior

The hybrid CP setup should run after the model has been fully constructed so it can properly configure the model's attention modules for context-parallel execution.
