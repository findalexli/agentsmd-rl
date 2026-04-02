# DP Engine Core Pause/Resume Deadlock

## Bug Description

There is a deadlock in the vLLM data-parallel (DP) engine core when requests arrive for already-completed waves while the scheduler is paused.

The issue occurs in `src/prime_rl/inference/patches.py`. The existing `transformers_v5_compat()` function serves as a vLLM general plugin that applies various monkey-patches for compatibility. However, it currently lacks a patch for a critical concurrency issue in vLLM's DP engine core.

## Problem Details

When a DP engine receives a request whose `request_wave` differs from `current_wave`, `EngineCore.add_request` can trigger a `start_wave` notification. This notification causes a `collective_rpc` call on other DP engines. However, if the local engine's scheduler is currently paused, it cannot participate in the collective operation — resulting in a deadlock where all DP engines wait on each other indefinitely.

The root cause is that the unpatched `add_request` method doesn't check whether the scheduler is paused before sending wave notifications, and doesn't properly coordinate the `engines_running` state.

## Relevant Context

- The fix should be a new monkey-patch function added to `src/prime_rl/inference/patches.py`
- The new patch should be wired into the existing `transformers_v5_compat()` plugin so it runs automatically in all vLLM processes
- The relevant vLLM internals are in `vllm.v1.engine.core` (`EngineCore`, `DPEngineCoreProc`) and `vllm.v1.core.sched.interface` (`PauseState`)
- The upstream vLLM fix is tracked at https://github.com/vllm-project/vllm/pull/37024

## Expected Behavior

- When a request arrives for a different wave and the scheduler is **unpaused**, the engine should send the start_wave notification (with `engines_running` set to True first)
- When the scheduler is **paused**, the engine must NOT send start_wave notifications to avoid the collective_rpc deadlock
- When `request_wave > current_wave`, `current_wave` should be updated regardless of pause state
