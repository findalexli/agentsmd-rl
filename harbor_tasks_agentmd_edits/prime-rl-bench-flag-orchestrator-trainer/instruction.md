# Add Performance Benchmarking Flag

## Problem

The project lacks a convenient way to benchmark the performance of the inference engine and trainer components. Users need to manually configure multiple settings to run benchmarks, which is error-prone and time-consuming.

## Task

Implement a `--bench` flag across the RL training system that:

1. **Trainer** (`src/prime_rl/trainer/config.py` and related files):
   - Add a `bench` field to `TrainerConfig`
   - Add an `auto_setup_bench` validator that automatically sets `max_steps=6` (1 warmup + 5 benchmark steps) and enables fake data if not already configured
   - Add a `print_benchmark` function to `src/prime_rl/trainer/utils.py` that displays benchmark results as a rich formatted table
   - Update `src/prime_rl/trainer/train.py` to call `print_benchmark` when in benchmark mode

2. **Orchestrator** (`src/prime_rl/orchestrator/config.py` and related files):
   - Rename the existing `validate_bench` validator to `auto_setup_bench`
   - Add warning log output when running in benchmark mode
   - Fix the column name in the benchmark output (change from `time/infer` to `time/orchestrator`)
   - Add necessary imports (e.g., `format_num`)

3. **RL Config** (`src/prime_rl/rl.py`):
   - Add a `bench` field to `RLConfig`
   - Add an `auto_setup_bench` validator that propagates the benchmark mode to both trainer and orchestrator
   - When in benchmark mode, configure the trainer's fake data to match the orchestrator's configuration (micro_batch_size, batch_size, seq_len)
   - When W&B is configured, suffix the project name with `-bench`

4. **Documentation** (`README.md`):
   - Add a "### Benchmarking" section documenting how to use the `--bench` flag
   - Include examples for:
     - Benchmarking inference (via orchestrator with running inference server)
     - Benchmarking the trainer standalone
     - Benchmarking a full RL run

## Files to Look At

- `src/prime_rl/trainer/config.py` — Trainer configuration
- `src/prime_rl/trainer/train.py` — Trainer entry point
- `src/prime_rl/trainer/utils.py` — Trainer utilities (add print_benchmark here)
- `src/prime_rl/orchestrator/config.py` — Orchestrator configuration
- `src/prime_rl/orchestrator/orchestrator.py` — Orchestrator entry point
- `src/prime_rl/orchestrator/utils.py` — Orchestrator utilities (benchmark table output)
- `src/prime_rl/rl.py` — RL configuration and orchestration
- `README.md` — Documentation (add Benchmarking section)

The key design pattern is using Pydantic's `@model_validator(mode="after")` to automatically configure benchmark settings when `bench=True` is set.
