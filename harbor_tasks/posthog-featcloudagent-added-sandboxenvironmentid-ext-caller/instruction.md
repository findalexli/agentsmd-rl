# feat(cloud-agent): expose sandbox_environment_id for external callers

## Problem

The `Task.create_and_run()` method in `products/tasks/backend/models.py` does not accept a `sandbox_environment_id` parameter. This means callers outside the internal agent-server flow cannot apply network restrictions (sandbox environments) when spawning tasks. The feature is tightly coupled to internal ph-code logic and unavailable to external products.

## Required Changes

### Code Changes

Modify `products/tasks/backend/models.py` in the `Task.create_and_run()` method to:

1. Accept an optional keyword-only parameter named `sandbox_environment_id` with type `str | None` defaulting to `None`

2. When `sandbox_environment_id` is provided (not None):
   - Look up the corresponding `SandboxEnvironment` record using `SandboxEnvironment.objects.filter(team=team, id=sandbox_environment_id).first()` and assign the result to a variable named `sandbox_env`
   - If the lookup returns no result (i.e., `sandbox_env` is None or falsy), raise `ValueError` with the exact message: `Invalid sandbox_environment_id: {sandbox_environment_id}`
   - Ensure `extra_state` is initialized using the pattern `extra_state = extra_state or {}` before adding values to it
   - Store the environment's ID in `extra_state` under the key `sandbox_environment_id` using the exact expression `str(sandbox_env.id)` (convert the environment's ID to string using the str() function)

### Documentation Update

After updating the code, update `docs/published/handbook/engineering/ai/sandboxed-agents.md`:

1. Add `sandbox_environment_id` to the Parameters table, documenting it as an optional string parameter that accepts a `SandboxEnvironment` ID
2. Include a usage example showing:
   - Creating a `SandboxEnvironment` with `SandboxEnvironment.objects.create()`
   - Configuring `network_access_level` and `allowed_domains`
   - Passing `sandbox_environment_id=str(env.id)` to `create_and_run()`

## Files to Look At

- `products/tasks/backend/models.py` — the `Task.create_and_run()` static method that needs the new parameter
- `docs/published/handbook/engineering/ai/sandboxed-agents.md` — engineering handbook documenting the sandboxed agent API
- `AGENTS.md` — project conventions including queryset filtering rules
