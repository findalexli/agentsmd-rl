# Bug: Slime router crashes with PD disaggregation and circuit breaker mismarks workers

## Context

The `_start_router` function in `slime/ray/rollout.py` is responsible for launching
either the slime router or the standard sglang router before rollout begins. It accepts
a `has_pd_disaggregation` flag indicating whether prefill-decode disaggregation is in use.

## Bug 1: Slime router + PD disaggregation

When a user configures PD disaggregation and the slime router (`args.use_slime_router=True`),
the function immediately crashes with an `AssertionError`. However, the slime router
now actually supports PD disaggregation — the hard assertion is outdated. The router
needs to be told that PD disaggregation is active so it can route prefill and decode
traffic correctly.

## Bug 2: Circuit breaker kills decode workers on transient timeouts

When using the standard sglang router (not slime router) with PD disaggregation,
RDMA transfer timeouts can occur transiently due to PCIe contention under high load.
The router's circuit breaker interprets these timeouts as dead decode workers and
removes them from the pool. This is incorrect — the timeouts are transient and the
workers recover. The circuit breaker should be disabled when PD disaggregation is active.

## Relevant code

- `slime/ray/rollout.py` — the `_start_router` function (around line 890-940)
- Look at both the `if args.use_slime_router:` and `else:` branches
