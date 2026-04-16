#!/bin/bash
set -e

cd /workspace/dagster

# Apply the gold patch using sed (more reliable for simple changes)
FILE="python_modules/libraries/dagster-aws/dagster_aws/pipes/clients/emr_serverless.py"

# Check if we're on base commit (buggy) or already fixed
if grep -q 'log_group = monitoring_configuration.get("logGroupName")' "$FILE"; then
    # Apply the fix using sed
    sed -i 's/log_group = monitoring_configuration.get("logGroupName") or "\/aws\/emr-serverless"/log_group = (\n            monitoring_configuration.get("cloudWatchLoggingConfiguration", {}).get("logGroupName")\n            or "\/aws\/emr-serverless"\n        )/' "$FILE"
    echo "Fix applied successfully"
else
    echo "Fix already applied or file has unexpected content"
    # Show the relevant line for debugging
    grep -n "log_group" "$FILE" || echo "No log_group line found"
fi
