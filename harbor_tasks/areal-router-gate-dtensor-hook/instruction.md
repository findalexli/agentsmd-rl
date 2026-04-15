# Fix: MoE router gate bypasses DTensor hooks breaking tensor parallelism

## Problem

The MoE (Mixture of Experts) router has a bug where DTensor hooks registered by `ReplicateParallel` never fire when the router gate is invoked. This breaks tensor parallelism setups.

## Required Behavior

1. **Gate module invocation**: Calling `router.forward(x)` must invoke the gate as a module so that any DTensor hooks (or other `nn.Module` hooks) registered on the gate module fire correctly.

2. **GEMM precision**: The gate computation must still use `router_gating_linear()` internally for dtype-aware GEMM when `router_dtype` is set.

3. **Checkpoint compatibility**: The gate's `state_dict()` keys must match a standard `nn.Linear(in_features, out_features, bias=False)` so existing checkpoints load correctly.

4. **Subclass requirement**: The gate must be an `nn.Linear` subclass. This subclass must have an `__init__` accepting `in_features`, `out_features`, and `router_dtype` parameters, and a `forward` method that delegates to `router_gating_linear` with the stored weight and `router_dtype`.

## Notes

- The repository CI requires ruff version 0.14.9 for linting and formatting checks on the experimental module.
- The gate's forward method must not be a stub — it must contain real computation logic.
- The `router_gating_linear` function performs dtype-aware GEMM and is defined in the same module as the router.
