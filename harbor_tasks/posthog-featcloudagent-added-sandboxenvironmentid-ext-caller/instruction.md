# feat(cloud-agent): expose sandbox_environment_id for external callers

## Problem

The `Task.create_and_run()` method in `products/tasks/backend/models.py` does not accept a `sandbox_environment_id` parameter. This means callers outside the internal agent-server flow cannot apply network restrictions (sandbox environments) when spawning tasks. The feature is tightly coupled to internal ph-code logic and unavailable to external products.

## Required Implementation

Modify `products/tasks/backend/models.py` in the `Task.create_and_run()` method to accept an optional `sandbox_environment_id` parameter with type `str | None` and default value `None` as a keyword-only argument.

When `sandbox_environment_id` is provided, the implementation must:

1. **Validate the SandboxEnvironment exists and belongs to the team**: Look up the environment using `SandboxEnvironment.objects.filter(id=sandbox_environment_id, team=team)`. Assign the query result to a variable named `sandbox_env`. Use the `.first()` method on the queryset to retrieve the environment.

2. **Raise ValueError with specific message**: If the lookup returns `None` (environment not found), raise a `ValueError` with the exact message: `Invalid sandbox_environment_id: {sandbox_environment_id}`

3. **Store in extra_state**: Before storing, ensure `extra_state` is initialized using the pattern `extra_state = extra_state or {}`. Store the sandbox environment ID in `extra_state` using bracket notation with the key `'sandbox_environment_id'` and the value `str(sandbox_env.id)`.

## Documentation Update

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
