# Improve worker management admin route

## Problem

The admin API endpoint at `apps/webapp/app/routes/admin.api.v1.workers.ts` for managing worker groups has limited functionality and a confusing parameter design. Currently:

1. **Creating a worker group always creates a new one** — there's no check for whether a group with the same name already exists, which can lead to duplicates or errors.
2. **The `makeDefaultForProjectId` parameter conflates two concerns** — it combines identifying the project with the action of making a group the default. This makes the API hard to extend.
3. **There's no way to remove a default worker group from a project** — once set, the only way to revert a project to the global default is direct database access.

## Expected Behavior

The admin workers endpoint should support three distinct operations:
- **Create a worker group** — with graceful handling when the group already exists (no token returned for existing groups)
- **Set a worker group as default for a project** — creating the group first if it doesn't exist
- **Remove the default worker group from a project** — reverting it to the global default

The API parameters should be redesigned so each operation is clearly expressed. Helper functions should be extracted for the core database operations (creating groups, setting defaults, removing defaults) with proper error handling.

## Files to Look At

- `apps/webapp/app/routes/admin.api.v1.workers.ts` — the admin route handler that needs the API improvements
- `apps/supervisor/README.md` — documents the worker group management API; must be updated to reflect the new parameters and capabilities

After making the code changes, update the supervisor README to clearly document all worker group management operations, including the new removal capability. The documentation should be reorganized for clarity with each operation in its own section.
