# Task: Fix Environment Variable Name Mismatch

## Problem

The enterprise service authentication is failing because the code is reading from an environment variable that doesn't match the Helm chart configuration.

The Helm chart is configured to inject `AUTOMATIONS_SERVICE_KEY` as the environment variable for service API authentication. However, the current implementation appears to be looking for a different variable name.

## Expected Behavior

After the fix:
- The service should read the API key from the `AUTOMATIONS_SERVICE_KEY` environment variable
- The health endpoint should report whether service authentication is configured based on whether `AUTOMATIONS_SERVICE_KEY` is set
- When authentication is not configured, the log message should reference `AUTOMATIONS_SERVICE_KEY`
- The authentication validation should compare incoming API keys against the value from `AUTOMATIONS_SERVICE_KEY`

## Files to Locate and Modify

Find and update the file in the enterprise server routes that handles service authentication. The file should reference the `AUTOMATIONS_SERVICE_KEY` environment variable consistently throughout:
- The module-level constant name
- The `os.getenv()` call
- The authentication validation logic
- The health check endpoint
- The module docstring
- Log messages

## Testing

The repository has existing unit tests at `enterprise/tests/unit/routes/test_service.py` that verify the expected behavior with the correct environment variable name.
