# Task: Add extension point for deployment validation

## Problem

The VCS GitHub Deployment class lacks an extension point for custom validation logic. Cloud-specific implementations need to inject checks (such as billing and block validation) between project validation and database operations, but no such hook exists today.

## Your Task

Add a protected hook method named `beforeCreateGitDeployment` to the `Deployment.php` file that subclasses can override to inject custom validation logic. The hook must be called within the `createGitDeployments` method after the `PROJECT_NOT_FOUND` validation check but before the DSN/database initialization.

The hook method must have this exact signature:

```php
protected function beforeCreateGitDeployment(Document $project, Document $repository, Database $dbForPlatform, Authorization $authorization): void
```

## Key Requirements

- Method name: `beforeCreateGitDeployment`
- Parameters (in this order): `Document $project`, `Document $repository`, `Database $dbForPlatform`, `Authorization $authorization`
- Return type: `void`
- Visibility: `protected` (to allow subclass overrides)
- Implementation: empty body (no-op base implementation)
- Call syntax: `$this->beforeCreateGitDeployment($project, $repository, $dbForPlatform, $authorization)`
- Placement: after the `PROJECT_NOT_FOUND` exception check, before the DSN creation line
- Follow existing code conventions in the file for formatting and style

## Relevant Files

- `src/Appwrite/Platform/Modules/VCS/Http/GitHub/Deployment.php` - The main file to examine and modify

## Agent Configuration Context

This repository has agent configuration files at the root level. Please review them for coding conventions:
- `CLAUDE.md` - Main project conventions (Action pattern, PSR-12 formatting, module structure)
- `AGENTS.md` - Project overview and commands
- `src/Appwrite/Platform/AGENTS.md` - Module structure and naming conventions

## Notes

- This is a PHP 8.3+ project using the Swoole runtime
- The codebase follows PSR-12 formatting (enforced by Pint)
- HTTP endpoint classes follow a specific Action pattern