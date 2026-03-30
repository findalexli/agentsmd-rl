# Fix: MoE router gate bypasses DTensor hooks breaking tensor parallelism

## Problem

The MoE (Mixture of Experts) router in `areal/experimental/models/archon/moe/router.py` uses `nn.Linear` for `self.gate`, but the `forward()` method bypasses it by calling `router_gating_linear(x, self.gate.weight, ...)` directly instead of `self.gate(x)`. This means DTensor hooks registered by `ReplicateParallel` never fire when the router gate is invoked, breaking tensor parallelism setups that rely on `ReplicateParallel`.

## Root Cause

The `TokenChoiceTopKRouter.__init__` creates `self.gate = nn.Linear(dim, num_experts, bias=False)`, but `forward()` calls the standalone `router_gating_linear()` function with `self.gate.weight` directly. DTensor hooks are registered at the module call level (`__call__`), so bypassing the module call means the hooks never trigger.

## Expected Behavior

The gate should be wrapped in a proper `nn.Module` subclass that delegates to `router_gating_linear()` inside its own `forward()`, so that calling `self.gate(x)` triggers both the gate computation and any registered DTensor hooks.

The fix should:
1. Create an `nn.Linear` subclass (e.g., `RouterGateLinear`) that wraps `router_gating_linear()` and accepts `router_dtype`
2. Replace `self.gate = nn.Linear(...)` with the new subclass
3. Replace `scores = router_gating_linear(x, self.gate.weight, self.router_dtype)` with `scores = self.gate(x)`
4. Maintain state dict compatibility with `nn.Linear(bias=False)` for checkpoint loading

## Files to Modify

- `areal/experimental/models/archon/moe/router.py`
