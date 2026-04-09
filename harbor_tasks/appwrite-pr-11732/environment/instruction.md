# Task: Add beforeCreateGitDeployment Hook

## Problem

The `Deployment.php` class in the VCS module handles creating deployments from GitHub webhooks. Currently, there's no way to add custom validation or pre-processing logic before a git deployment is created. The Cloud version of Appwrite needs to enforce billing checks and block validation before allowing deployments.

## What You Need to Do

Add an extensibility hook called `beforeCreateGitDeployment()` to the `Deployment` class that:

1. **Location**: `src/Appwrite/Platform/Modules/VCS/Http/GitHub/Deployment.php`

2. **Method signature**: Create a protected method with these exact parameters in this order:
   - `Document $project` - The project document
   - `Document $repository` - The repository document
   - `Database $dbForPlatform` - Platform database instance
   - `Authorization $authorization` - Authorization instance
   - Return type: `void`

3. **Call site**: The method should be invoked in `createGitDeployments()` after the project is validated (after the `PROJECT_NOT_FOUND` check) but before database operations begin.

4. **Implementation**: The base implementation should be empty (no-op) since it's designed to be overridden in Cloud-specific subclasses.

## Context

The `createGitDeployments()` method processes incoming git push events and creates deployments. The hook should allow Cloud to inject billing/blocking validation without modifying the core deployment flow.

Look at the existing method `getBuildQueueName()` in the same class as a reference for the method signature pattern and parameter ordering.

## Requirements

- The hook method must have the exact signature specified
- The hook must be called with all four parameters in the correct order
- The base implementation must be empty (extensibility point)
- The call must happen after project validation in the deployment flow
