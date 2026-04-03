# Add sandbox_environment_id support to Task.create_and_run

## Problem

The `Task.create_and_run()` method in `products/tasks/backend/models.py` currently has no way for external callers to specify network restrictions when spawning a sandboxed agent. The `SandboxEnvironment` model already exists and controls network access (trusted domains, custom allowlists), but there's no way to pass an environment ID through the task creation API.

Product teams that want to restrict an agent's network access have to work around this by setting up environments separately and hoping the temporal workflow picks them up — there's no direct coupling.

## Expected Behavior

`Task.create_and_run()` should accept an optional `sandbox_environment_id` parameter. When provided, it should:
1. Validate the ID against the `SandboxEnvironment` model (scoped to the same team)
2. Raise an error if the ID is invalid or doesn't belong to the team
3. Pass the environment ID through to the task run so the temporal workflow can apply the network restrictions

After making the code change, update the sandboxed agents handbook documentation at `docs/published/handbook/engineering/ai/sandboxed-agents.md` to reflect the new parameter. The parameters table and the network access section should explain how external callers can use this feature.

## Files to Look At

- `products/tasks/backend/models.py` — the `Task` model and `create_and_run()` static method
- `docs/published/handbook/engineering/ai/sandboxed-agents.md` — handbook docs for sandboxed agents API
