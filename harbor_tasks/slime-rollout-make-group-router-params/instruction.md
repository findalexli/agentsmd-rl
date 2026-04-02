# Bug: `_make_group` in rollout server startup captures router details via closure

## Summary

In `slime/ray/rollout.py`, the `start_rollout_servers` function defines a nested helper
`_make_group` that constructs `ServerGroup` objects for each engine group. This helper
references `router_ip` and `router_port` from the enclosing scope (closure) rather than
receiving them as explicit parameters.

## Problem

When running a multi-model configuration — especially with encoder-prefill disaggregation
(EPD) — the enclosing `for model_idx, model_cfg in enumerate(config.models)` loop reassigns
`router_ip` and `router_port` on each iteration via `_start_router(...)`. Because Python
closures capture the *variable* (not the *value*), any deferred or reordered execution of
`_make_group` can silently use stale router coordinates from a previous or subsequent model
iteration.

Even in the current sequential flow, this coupling is fragile: a future refactor (e.g.,
launching groups asynchronously) would silently break routing without any clear error.

## Where to look

- `slime/ray/rollout.py` — the `_make_group` function definition and its three call sites
  (encoder-group loop, non-encoder-group loop, and the non-EPD fallback loop).

## Expected behaviour

Each engine group must always be connected to the correct router for its model, regardless
of how many models are configured or in what order groups are started. The dependency on
the router coordinates should not rely on mutable closure state.
