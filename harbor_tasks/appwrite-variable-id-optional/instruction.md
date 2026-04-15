# Bug: Creating Project Variables Fails Due to Mandatory variableId Parameter

## Problem

Creating a global project variable via the `POST /v1/project/variables` endpoint fails with the error message:

> "Param 'variableId' is not optional"

This occurs because the API endpoint marks `variableId` as a required parameter, but the Console UI does not provide a `variableId` when creating variables through Settings > Global variables.

## Expected Behavior

When no `variableId` is provided in the request, the endpoint should automatically generate one using `ID::unique()`, matching the behavior of the `createVariable` endpoints for Functions and Sites.

The fix should ensure:
- The `variableId` parameter is optional (the optional flag should be `true`)
- The default value for `variableId` is `'unique()'`
- The `CustomId` validator continues to be used for the parameter
- The `action()` method logic remains unchanged (it already handles `'unique()'` correctly)
- PSR-12 formatting standards are maintained

## Constraints

- Do NOT modify the validator logic - keep using `CustomId`
- Do NOT modify the `action()` method - it already handles `'unique()'` correctly
- Maintain PSR-12 formatting standards
