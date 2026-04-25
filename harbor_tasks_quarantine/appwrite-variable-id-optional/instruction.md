# Bug: Creating Project Variables Fails Due to Mandatory variableId Parameter

## Problem

Creating a global project variable via the `POST /v1/project/variables` endpoint fails with the error:

> "Param 'variableId' is not optional"

This error occurs because the API endpoint requires `variableId`, but the Console UI does not provide this parameter when creating variables through Settings > Global variables. The same endpoint in Functions and Sites modules handles missing `variableId` correctly.

## Expected Behavior

When `variableId` is not provided in the request, the endpoint should automatically generate one using `ID::unique()`, matching the behavior of the `createVariable` endpoints for Functions and Sites.

The endpoint should:
- Accept requests without `variableId`
- Generate a unique ID automatically when `variableId` is omitted
- Validate any provided `variableId` using the `CustomId` validator
- Pass all existing CI checks

## Target File

The endpoint is implemented in:
```
src/Appwrite/Platform/Modules/Project/Http/Project/Variables/Create.php
```

## CI/CD Verification

After making changes, ensure these checks pass:
- `composer validate --no-check-publish` passes
- Laravel Pint PSR-12 linting passes on the modified file
- PHPStan static analysis passes on the modified file
- `phpunit tests/unit/Utopia/Database/Validator/CustomIdTest.php` passes

## Constraints

- Do NOT modify the `action()` method - it already handles generated IDs correctly
- Do NOT modify any existing validator logic
- Maintain PSR-12 formatting standards