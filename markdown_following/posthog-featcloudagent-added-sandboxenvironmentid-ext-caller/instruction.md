# feat(cloud-agent): expose sandbox_environment_id for external callers

## Problem

The `Task.create_and_run()` method in `products/tasks/backend/models.py` does not accept a `sandbox_environment_id` parameter. This means callers outside the internal agent-server flow cannot apply network restrictions (sandbox environments) when spawning tasks. The feature is tightly coupled to internal ph-code logic and unavailable to external products.

## Required Changes

### Code Changes

Modify `products/tasks/backend/models.py` in the `Task.create_and_run()` method to:

1. Accept an optional keyword-only parameter named `sandbox_environment_id` with type `str | None` defaulting to `None`

2. When `sandbox_environment_id` is provided (not None):
   - Look up the corresponding `SandboxEnvironment` record by filtering on both the provided ID and the team, ensuring the environment belongs to the current team (not another team's environment)
   - If the lookup finds no matching environment, raise a `ValueError` with a message that helps the caller identify which ID was invalid
   - Before storing values in `extra_state`, ensure it is initialized to an empty dict if not already provided
   - Store the environment's string ID in `extra_state` under the key `sandbox_environment_id` so temporal workflows and downstream code can reference it

### Documentation Update

After updating the code, update `docs/published/handbook/engineering/ai/sandboxed-agents.md`:

1. Add `sandbox_environment_id` to the Parameters table, documenting it as an optional string parameter that accepts a `SandboxEnvironment` ID
2. Include a usage example showing:
   - Creating a `SandboxEnvironment` with `SandboxEnvironment.objects.create()`
   - Configuring `network_access_level` and `allowed_domains`
   - Passing `sandbox_environment_id` to `create_and_run()` with the environment's ID converted to string

## Files to Look At

- `products/tasks/backend/models.py` — the `Task.create_and_run()` static method that needs the new parameter
- `docs/published/handbook/engineering/ai/sandboxed-agents.md` — engineering handbook documenting the sandboxed agent API
- `AGENTS.md` — project conventions including queryset filtering rules

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
