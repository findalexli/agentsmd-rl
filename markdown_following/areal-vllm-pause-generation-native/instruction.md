# Bug: AReaL vLLM server uses fragile monkey-patching for request pausing and weight updates

## Context

The AReaL vLLM server (`areal/engine/vllm_ext/areal_vllm_server.py`) manages request pausing and weight update flows during RL training. Currently, it patches `EngineCore` internals at module load time via a `hook()` function. This monkey-patches methods like `abort_all_reqs`, `areal_injected_update_weight`, and related functions onto `EngineCore` using `setattr`.

The monkey-patched methods manually abort requests by walking the scheduler's `running` and `waiting` queues, constructing `EngineCoreOutput` objects with `FinishReason.ABORT`, and pushing them into the output queue.

## Problem

This custom approach has several issues:

1. **Multi-node breakage**: In multi-node deployments, the injected hook only executes on the head node. Other nodes never receive the abort/pause signal, causing weight update failures.

2. **Occasional hangs**: The custom abort path can deadlock when interacting with vLLM's internal scheduling, particularly under concurrent request load.

3. **Maintenance burden**: The monkey-patching relies on these vLLM v1 internals which are fragile across vLLM version upgrades:
   - `EngineCore`
   - `EngineCoreOutput`
   - `EngineCoreOutputs`
   - `FinishReason`
   - `RequestStatus`
   - `LoRARequestStates`

4. **Incomplete pause/resume handling**: The weight update endpoints call `llm.engine_core.call_utility_async()` to invoke injected methods, but this bypasses the proper pause/resume lifecycle. When weight updates occur while requests are in flight, the scheduler state becomes inconsistent.

5. **Continue endpoint doesn't resume**: The `areal_continue_generation` endpoint sets an internal event flag but never tells the engine client to actually resume generation.

## Symptoms to fix

- The file contains a `hook()` function and `setattr(EngineCore, ...)` calls that should be removed
- The file contains a standalone `abort_all_reqs()` function that should be removed
- The file imports these vLLM v1 internals that should be removed:
  - `EngineCore`
  - `EngineCoreOutput`
  - `EngineCoreOutputs`
  - `FinishReason`
  - `RequestStatus`
  - `LoRARequestStates`
- Weight update endpoints (`areal_update_weight`, `areal_update_weight_lora`, `areal_update_weight_xccl`, `areal_update_weight_lora_xccl`) call `llm.engine_core.call_utility_async()` without properly pausing and resuming generation
- The `areal_pause_generation` endpoint calls `llm.engine_core.call_utility_async("abort_all_reqs")` instead of using the engine client's native pause capability
- The `areal_continue_generation` endpoint never calls the engine client's resume method

## Required API routes and models to preserve

The following API route paths must remain declared:
- `/areal_update_weights`
- `/areal_update_weights_lora`
- `/areal_update_weights_xccl`
- `/areal_update_weights_lora_xccl`
- `/areal_init_weights_update_group`
- `/areal_set_update_weight_meta`
- `/areal_set_update_weight_meta_lora`
- `/areal_pause_generation`
- `/areal_continue_generation`
- `/v1/completions`

The following Pydantic request model classes must remain defined:
- `UpdateWeightsRequest`
- `UpdateWeightsRequestLora`
- `UpdateGroupRequest`
- `UpdateWeightsFromXcclRequest`
- `UpdateWeightsFromXcclRequestLora`

## Acceptance criteria

1. The `hook()` function is removed
2. All `setattr(EngineCore, ...)` calls are removed
3. The standalone `abort_all_reqs()` function is removed
4. The imports of `EngineCore`, `EngineCoreOutput`, `EngineCoreOutputs`, `FinishReason`, `RequestStatus`, and `LoRARequestStates` are removed
5. The weight update endpoints properly pause generation before performing RPC calls and resume generation afterward (even when the RPC fails). The pause must not wait for in-flight requests to finish and must clear the prefix cache.
6. The `areal_pause_generation` endpoint uses the engine client's native pause capability instead of routing through `engine_core.call_utility_async`
7. The `areal_continue_generation` endpoint invokes the engine client's native resume method in addition to setting the event flag
8. All existing API route paths and Pydantic request model classes are preserved
9. The modified file passes linting, type checking, and formatting requirements

## Code Style Requirements

- Python code must pass `ruff check` (linting and import sorting via `ruff check --select I`)
- Python code must pass `ruff format --check` (code formatting)
- No trailing whitespace anywhere in the file
- File must end with exactly one newline character
- No wildcard imports (`from x import *`)
- All async endpoint function parameters must have explicit type annotations
