# Fix EMR Serverless Log Group Name Lookup

## Problem

The `PipesEMRServerlessClient` in `dagster_aws/pipes/clients/emr_serverless.py` is incorrectly reading the CloudWatch log group name from EMR Serverless API's monitoring configuration.

**Symptom:** When a custom log group is configured via EMR Serverless API's `cloudWatchLoggingConfiguration.logGroupName` field, the code ignores it and always falls back to the default `/aws/emr-serverless` log group. This prevents log streaming from working with custom CloudWatch log groups.

## Expected Behavior

The code should:
1. When `cloudWatchLoggingConfiguration` contains a `logGroupName` value, use that custom log group
2. When no custom log group is configured, fall back to `/aws/emr-serverless`

Example configurations the code should handle:

```python
# Custom log group configured - should extract "/custom/log/group"
{
    "cloudWatchLoggingConfiguration": {
        "enabled": True,
        "logGroupName": "/custom/log/group"
    }
}

# No logGroupName in cloudWatchLoggingConfiguration - should fall back to "/aws/emr-serverless"
{
    "cloudWatchLoggingConfiguration": {
        "enabled": True
    }
}

# Missing cloudWatchLoggingConfiguration entirely - should fall back to "/aws/emr-serverless"
{}
```

## Files to Modify

- `python_modules/libraries/dagster-aws/dagster_aws/pipes/clients/emr_serverless.py`

## Verification

- After making the fix, run `make ruff` from the repository root to ensure code quality
- The fallback to `/aws/emr-serverless` must be preserved when no custom log group is configured
