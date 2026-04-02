# Bug: AReaL vLLM server uses fragile monkey-patching for request pausing and weight updates

## Context

The AReaL vLLM server (`areal/engine/vllm_ext/areal_vllm_server.py`) manages request pausing and weight update flows during RL training. Currently, it patches `EngineCore` internals at module load time — injecting custom `abort_all_reqs`, `areal_injected_update_weight`, and related methods via `setattr`. These monkey-patched methods manually abort requests by walking the scheduler's `running` and `waiting` queues, constructing `EngineCoreOutput` objects with `FinishReason.ABORT`, and pushing them into the output queue.

## Problem

This custom abort-and-update approach has several issues:

1. **Multi-node breakage**: In multi-node deployments (e.g., large models like Qwen3-235B), the injected hook only executes on the head node. Other nodes never receive the abort/pause signal, causing weight update failures.

2. **Occasional hangs**: The custom abort path can deadlock when interacting with vLLM's internal scheduling, particularly under concurrent request load.

3. **Maintenance burden**: The monkey-patching relies on vLLM v1 internals (`EngineCore`, `EngineCoreOutput`, `EngineCoreOutputs`, `FinishReason`, `RequestStatus`, `LoRARequestStates`). These are fragile across vLLM version upgrades.

4. **Incomplete continue_generation**: The `areal_continue_generation` endpoint only sets the internal event flag but never tells the engine client to actually resume, so the engine stays paused from its perspective.

## What needs to change

vLLM now provides native APIs on the engine client for pausing and resuming generation that handle request draining and prefix cache reset across all nodes. The weight update endpoints and the pause/continue endpoints should use these upstream mechanisms instead of the custom monkey-patched approach.

The legacy `hook()` function and all the functions it patches onto `EngineCore` are no longer needed and should be removed, along with the imports they require.

## Files to modify

- `areal/engine/vllm_ext/areal_vllm_server.py`

## Acceptance criteria

- Weight update endpoints (`areal_update_weights`, `areal_update_weights_lora`, `areal_update_weights_xccl`, `areal_update_weights_lora_xccl`) pause generation before the RPC and resume it afterward (even on failure)
- `areal_pause_generation` uses the native pause API
- `areal_continue_generation` calls the native resume API
- No monkey-patching of `EngineCore` remains
- Unused imports related to the removed code are cleaned up
- All existing endpoint routes and external behavior are preserved
