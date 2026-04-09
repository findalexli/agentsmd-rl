# Add Trackio Experiment Tracking Backend

## Problem

AReaL currently supports WandB, SwanLab, and TensorBoard for experiment tracking, but there is no support for [Trackio](https://github.com/gradio-app/trackio) — a lightweight, local-first experiment tracking library from Hugging Face with a wandb-compatible API. Users want to be able to track experiments using Trackio, which supports local dashboards and Hugging Face Spaces deployment.

## Expected Behavior

A new `TrackioConfig` dataclass should be added to the configuration system, following the same patterns as the existing tracking backends (`WandBConfig`, `SwanlabConfig`, `TensorBoardConfig`). The config should support at minimum:
- A mode field (`"disabled"`, `"online"`, `"local"`) defaulting to disabled
- Project name and run name fields
- A space ID field for HF Spaces deployment

The `StatsLogger` class should integrate trackio for the full lifecycle: initialization, logging metrics on each commit, and cleanup on close. The combined logging helper function in `logging.py` should also include trackio with a graceful fallback when the package is not installed.

## Files to Look At

- `areal/api/cli_args.py` — Configuration dataclasses; look at how `TensorBoardConfig` and `StatsLoggerConfig` are structured
- `areal/utils/stats_logger.py` — `StatsLogger` class that manages experiment tracking backends (init, commit, close lifecycle)
- `areal/utils/logging.py` — Combined logging helper function that logs to multiple backends
- `pyproject.toml` — Project dependencies
