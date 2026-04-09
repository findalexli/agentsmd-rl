# Bug: Creating Project Variables Fails Due to Mandatory variableId Parameter

## Problem

Creating a global project variable via the `POST /v1/project/variables` endpoint always fails with the error message:

> "Param 'variableId' is not optional"

This happens because the Console UI does not send a `variableId` when creating variables through Settings > Global variables, but the API endpoint incorrectly marks this parameter as required.

## Expected Behavior

When no `variableId` is provided, the endpoint should automatically generate one using `ID::unique()`, similar to how the `createVariable` endpoints for Functions and Sites work.

## File to Modify

**`src/Appwrite/Platform/Modules/Project/Http/Project/Variables/Create.php`**

## Hints

- Look at the `->param()` call for `variableId` in the constructor
- The second argument is the default value, the fifth argument controls whether the param is optional (`true` = optional)
- The `action()` method already has logic to handle `'unique()'` - it just needs the parameter to be optional for it to be reachable
- Check how other similar endpoints (Functions/Variables/Create.php or Sites/Variables/Create.php) define their `variableId` parameter for reference

## Constraints

- Do NOT change the validator logic - keep using `CustomId`
- Do NOT modify the `action()` method - the fix is only in the `__construct()` method's param definition
- Maintain PSR-12 formatting standards
