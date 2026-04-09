# Task: Rename Environment Variable

## Problem

The enterprise service routes in `enterprise/server/routes/service.py` are reading the service API key from an environment variable with the wrong name. The code currently uses `AUTOMATIONS_SERVICE_API_KEY` but should use `AUTOMATIONS_SERVICE_KEY` to match the helm chart configuration.

## What Needs to Change

Update `enterprise/server/routes/service.py` to:

1. Change the module-level constant from `AUTOMATIONS_SERVICE_API_KEY` to `AUTOMATIONS_SERVICE_KEY`
2. Update the `os.getenv()` call to read from `'AUTOMATIONS_SERVICE_KEY'` instead of `'AUTOMATIONS_SERVICE_API_KEY'`
3. Update the `validate_service_api_key` function to use the new variable name
4. Update the `service_health` function to use the new variable name
5. Update the module docstring to reference the correct environment variable name
6. Update log messages that reference the old environment variable name

## Files to Modify

- `enterprise/server/routes/service.py` - Main file requiring changes

## Expected Behavior

After the change:
- The code should read the service API key from the `AUTOMATIONS_SERVICE_KEY` environment variable
- All references to the old variable name should be removed
- The health endpoint should correctly report `service_auth_configured` based on the new env var
- The authentication validation should work with the new env var name

## Notes

- This is a simple rename/refactor - no functional logic changes needed
- The tests in `enterprise/tests/unit/routes/test_service.py` have already been updated to use the new name (you don't need to modify tests)
- Focus only on `enterprise/server/routes/service.py`
