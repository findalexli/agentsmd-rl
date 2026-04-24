# VCS GitHub Deployment Validation Hook

## Goal

Add an extensible hook method to the GitHub Deployment class that allows subclasses (such as Appwrite Cloud implementations) to inject custom logic before database operations during deployment creation.

## Requirements

1. **Method signature**: A protected method with exactly 4 parameters: the project document, repository document, database instance, and authorization context. The method returns void.

2. **Placement**: The method must be called from within `createGitDeployments` at the insertion point that lies after the project existence validation (the `PROJECT_NOT_FOUND` check) and before the database connection is instantiated (`new DSN`).

3. **Implementation**: The base class implementation should be a no-op (empty body) so that subclasses can override it with custom behavior.

4. **Naming convention**: The method name follows the `before<Operation>` pattern used for extensibility hooks in this codebase.

## Target file

`src/Appwrite/Platform/Modules/VCS/Http/GitHub/Deployment.php`

## Context

Appwrite Cloud extensions need to perform custom validation or setup before deployment creation. Currently there is no extension point at this stage in the `createGitDeployments` flow. Adding this hook enables Cloud-specific subclasses to inject logic without modifying the core deployment logic.

## Verification

Your implementation will be checked for:
- The method exists with the correct name, parameter count, and protected visibility
- The method is called at the correct point in `createGitDeployments` (between the project validation check and the database instantiation)
- The base class implementation is empty
- PHP syntax remains valid and Composer autoload continues to work