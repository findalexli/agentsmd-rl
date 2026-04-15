# Fix: MoE router gate bypasses DTensor hooks breaking tensor parallelism

## Problem

The MoE (Mixture of Experts) router in `areal/experimental/models/archon/moe/router.py` has a bug where DTensor hooks registered by `ReplicateParallel` never fire when the router gate is invoked.

`TokenChoiceTopKRouter.__init__` creates `self.gate = nn.Linear(dim, num_experts, bias=False)`, but `forward()` calls the standalone function `router_gating_linear(x, self.gate.weight, self.router_dtype)` directly instead of invoking `self.gate(x)`. Since DTensor hooks are registered at the module call level (`__call__`), bypassing the module means the hooks never trigger, breaking tensor parallelism setups.

## Required Behavior

1. **Gate module invocation**: Calling `router.forward(x)` must invoke the gate as a module (i.e., `self.gate(x)`) so that any DTensor hooks (or other `nn.Module` hooks) registered on `self.gate` fire correctly.

2. **GEMM precision**: The gate computation must still use `router_gating_linear()` internally for dtype-aware GEMM when `router_dtype` is set.

3. **Checkpoint compatibility**: `router.gate.state_dict()` keys must match `nn.Linear(dim, num_experts, bias=False)` so existing checkpoints load correctly.

4. **Class requirement**: The gate must be implemented as a subclass of `nn.Linear` named `RouterGateLinear`. This subclass must have an `__init__` that accepts `in_features`, `out_features`, and `router_dtype` parameters, and a `forward` method that delegates to `router_gating_linear`.

## Files to Look At

- `areal/experimental/models/archon/moe/router.py` -- contains `TokenChoiceTopKRouter` and the standalone `router_gating_linear()` function