# Fix: MoE router gate bypasses DTensor hooks breaking tensor parallelism

## Problem

The MoE (Mixture of Experts) router in `areal/experimental/models/archon/moe/router.py` has a bug where DTensor hooks registered by `ReplicateParallel` never fire when the router gate is invoked.

`TokenChoiceTopKRouter.__init__` creates `self.gate = nn.Linear(dim, num_experts, bias=False)`, but `forward()` calls the standalone function `router_gating_linear(x, self.gate.weight, self.router_dtype)` directly instead of invoking `self.gate(x)`. Since DTensor hooks are registered at the module call level (`__call__`), bypassing the module means the hooks never trigger, breaking tensor parallelism setups.

## Expected Behavior

Calling `router.forward(x)` should invoke the gate as a module so that any DTensor hooks (or other `nn.Module` hooks) registered on `self.gate` fire correctly. The gate computation should still use `router_gating_linear()` for dtype-aware GEMM, and checkpoint compatibility with `nn.Linear(bias=False)` state dicts must be preserved.

## Files to Look At

- `areal/experimental/models/archon/moe/router.py` -- contains `TokenChoiceTopKRouter` and the standalone `router_gating_linear()` function
