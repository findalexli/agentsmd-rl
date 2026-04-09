# feat(cloud-agent): expose sandbox_environment_id for external callers

## Problem

The `Task.create_and_run()` method in `products/tasks/backend/models.py` does not accept a `sandbox_environment_id` parameter. This means callers outside the internal agent-server flow cannot apply network restrictions (sandbox environments) when spawning tasks. The feature is tightly coupled to internal ph-code logic and unavailable to external products.

## Expected Behavior

The `create_and_run()` method should accept an optional `sandbox_environment_id` parameter. When provided, it should:
1. Validate that the `SandboxEnvironment` exists and belongs to the correct team
2. Raise a descriptive `ValueError` if the ID is invalid
3. Store the environment ID in the task run's `extra_state` so downstream workflows can enforce network restrictions

After updating the code, the relevant engineering documentation should be updated to reflect this new capability. The handbook doc at `docs/published/handbook/engineering/ai/sandboxed-agents.md` should document the new parameter in the parameters table and include a usage example showing how external callers can create a `SandboxEnvironment` and pass its ID to `create_and_run`.

## Files to Look At

- `products/tasks/backend/models.py` — the `Task.create_and_run()` static method that needs the new parameter
- `docs/published/handbook/engineering/ai/sandboxed-agents.md` — engineering handbook documenting the sandboxed agent API
- `AGENTS.md` — project conventions including queryset filtering rules
