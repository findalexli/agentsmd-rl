# Task: Add Anonymous User ID to Telemetry

## Problem

Dagster's telemetry system currently tracks events with an `instance_id` that varies based on the `DAGSTER_HOME` environment variable. This makes it impossible to consistently identify the same user across different Dagster instances (e.g., when they work on multiple projects with different `DAGSTER_HOME` values).

## Symptoms

1. When users run Dagster from different project directories (each with its own `DAGSTER_HOME`), each project generates a different `instance_id`, making it appear as if different users are using Dagster.

2. The telemetry system lacks a stable, user-level identifier that persists across all Dagster instances on the same machine.

3. The `TelemetryEntry` NamedTuple currently only tracks instance-level identifiers, not user-level identifiers.

## Required Behavior

Your implementation must satisfy the following requirements (verified by tests):

1. **Export `USER_ID_STR` constant** with value `"user_id"` from the telemetry module, matching the existing pattern for `INSTANCE_ID_STR = "instance_id"`.

2. **User ID generation and retrieval**:
   - Create a function that returns a valid UUID string for each user
   - The user ID must be persistent across multiple calls
   - If the user ID cannot be created or retrieved, the function must return the literal error placeholder string: `<<unable_to_set_user_id>>`

3. **Storage location**:
   - Store the user ID in a YAML file at `~/.dagster/.telemetry/user_id.yaml`
   - The path to the telemetry directory must contain `.dagster/.telemetry` in its string representation
   - The user ID must NOT be stored in `$DAGSTER_HOME` - it should be completely independent of that environment variable
   - The YAML file must have a key named `"user_id"` containing the user ID string

4. **`TelemetryEntry` NamedTuple**:
   - Must include a `"user_id"` field in its `_fields` tuple
   - Must accept a `user_id` string parameter when constructing instances

5. **Telemetry payloads**:
   - All telemetry payloads must include the `user_id` field alongside `instance_id`

## Implementation Guidance

Look at how `instance_id` is currently implemented in the telemetry system:
- It uses `dagster_shared.telemetry` module for core functionality
- It uses YAML for persistence
- It integrates with `dagster._core.telemetry` for Dagster proper
- It integrates with `dagster_dg_core.utils.telemetry` for the dg CLI

The user ID should follow a similar pattern but be stored in the user's home directory (`~/.dagster/.telemetry/`) rather than in `$DAGSTER_HOME`, ensuring it remains consistent regardless of which Dagster project the user is working on.

## Testing Expectations

Your solution will be tested for:
- Returning a valid, non-empty UUID string (not the error placeholder)
- Persistence across multiple calls
- Storage in `~/.dagster/.telemetry/` (not in `DAGSTER_HOME`)
- Consistency when `DAGSTER_HOME` changes
- `TelemetryEntry` having the `user_id` field
- Telemetry payloads including `user_id`

## Notes

- The user ID is meant to be anonymous and consistent across all Dagster instances for a given user
- Follow the existing code style in the telemetry modules
- Use top-level imports where possible and add type annotations per the repo's conventions
