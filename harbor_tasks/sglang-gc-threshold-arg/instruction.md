# Feature Request: Configurable Garbage Collection Thresholds

## Problem

SGLang's inference engine currently uses Python's default garbage collection thresholds. For latency-sensitive online serving workloads with strict p99 SLO requirements, the default GC behavior triggers collections too frequently — each collection can take hundreds of milliseconds, causing latency spikes.

There is no way to tune the GC collection frequency from the command line or `ServerArgs`.

## Expected Behavior

Users should be able to pass a `--gc-threshold` argument (accepting 1 to 3 integers) when launching the engine. The engine should:

1. Accept the argument via `ServerArgs` and the CLI argument parser
2. Validate that 1–3 integers are provided (raise an error otherwise)
3. Apply the thresholds using Python's `gc.set_threshold()` early in the subprocess launch sequence (in `_launch_subprocesses`)

## Relevant Files

- `python/sglang/srt/server_args.py` — `ServerArgs` dataclass and `add_cli_args()` / `check_server_args()` methods
- `python/sglang/srt/entrypoints/engine.py` — `_launch_subprocesses()` function where engine initialization happens
