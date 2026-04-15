# Add Trackio Experiment Tracking Backend

## Problem

AReaL currently supports WandB, SwanLab, and TensorBoard for experiment tracking, but there is no support for [Trackio](https://github.com/gradio-app/trackio) — a lightweight, local-first experiment tracking library from Hugging Face with a wandb-compatible API. Users want to be able to track experiments using Trackio, which supports local dashboards and Hugging Face Spaces deployment.

## Expected Behavior

A new `TrackioConfig` dataclass should be added to the configuration system, following the same patterns as the existing tracking backends (`WandBConfig`, `SwanlabConfig`, `TensorBoardConfig`). The config should support:
- A mode field with exactly three valid values: `"disabled"`, `"online"`, and `"local"`. The default must be `"disabled"`. Invalid modes must raise `ValueError` with a descriptive message.
- Project name field (optional, can default to `None`)
- Run name field (optional, can default to `None`)
- A space ID field for HF Spaces deployment (optional, can default to `None`)

The `StatsLogger` class should integrate trackio for the full lifecycle:
- On `init()`: if trackio mode is not `"disabled"`, call `trackio.init(project=..., name=...)` with the project and name from the trackio config (falling back to experiment_name and trial_name respectively)
- On `commit()`: call `trackio.log(item, step=...)` for each log entry when trackio is enabled
- On `close()`: call `trackio.finish()` when trackio is enabled

The combined logging helper function in `logging.py` should also call `trackio.log(data, step=...)` with a graceful fallback (try/except with `pass`) when trackio is not installed.

## Files to Look At

- `areal/api/cli_args.py` — Configuration dataclasses; look at how `TensorBoardConfig` and `StatsLoggerConfig` are structured
- `areal/utils/stats_logger.py` — `StatsLogger` class that manages experiment tracking backends (init, commit, close lifecycle)
- `areal/utils/logging.py` — Combined logging helper function that logs to multiple backends
- `pyproject.toml` — Project dependencies
