# Task: Refactor domainVerification and cookieDomain from Global Config to Request-Scoped Resources

## Problem
The codebase currently stores `domainVerification` and `cookieDomain` in global mutable state via `Config::setParam()` and `Config::getParam()`. These values are derived from request-specific data (hostname, origin, project context), so using global config forces mutation of global state on each request. This is an anti-pattern that should be refactored to use request-scoped dependency injection.

## Background
The application uses Utopia PHP's `Http::setResource()` system for defining request-scoped resources and the `->inject()` method for dependency injection into controller actions. You should familiarize yourself with how existing resources are defined in the initialization layer and how controllers receive injected dependencies.

## Required Changes

### New Resources to Define

You must define two request-scoped resources:

1. **`domainVerification`** (resource name)
   - Must return a `bool` indicating whether the request origin's registerable domain matches the request hostname's registerable domain
   - Depends on the `Request` object
   - Must use the `Utopia\Domains\Domain` class to parse and compare domains
   - Logic: Compare `getRegisterable()` of hostname vs origin hostname; return true only if both match AND are non-empty

2. **`cookieDomain`** (resource name)
   - Must return `?string` (nullable string) - the cookie domain or `null` for localhost/IP addresses
   - Depends on both the `Request` object and the `project` document
   - Must handle these specific cases:
     - Return `null` when hostname is `localhost` or matches pattern `localhost:{port}`
     - Return `null` when hostname is a valid IP address (detect using `FILTER_VALIDATE_IP`)
     - Return `null` for migration hosts defined in `_APP_MIGRATION_HOST` environment variable
     - Return `.` + registerable domain (via `Domain` class) when project ID is `console` AND `_APP_CONSOLE_ROOT_SESSION` env var equals `enabled`
     - Return `.` + hostname for all other cases

### Code Patterns to Eliminate

The following patterns indicate the old global-state approach and must be eliminated:
- `Config::setParam('domainVerification', ...)` - setting global config
- `Config::setParam('cookieDomain', ...)` - setting global config
- `Config::getParam('domainVerification')` - reading global config
- `Config::getParam('cookieDomain')` - reading global config

### Controllers Requiring Injection

Controller actions that need these values must:
- Inject the resources using `->inject('domainVerification')` and `->inject('cookieDomain')` in the action chain
- Accept `bool $domainVerification` and `?string $cookieDomain` as parameters in the action callback
- Use the injected parameters instead of `Config::getParam()` calls

### Closures Requiring Updates

Any closures (such as `$createSession`) that use these values must be updated to accept them as parameters.

## Files Likely Involved

Based on the problem description, you should examine:
- Resource initialization files (where `Http::setResource()` calls are defined)
- General controller/router files (where global config mutations likely occur)
- Account-related API controllers (where session/cookie handling occurs)
- Team membership controllers (where invitation acceptance and session creation occurs)

## Verification Criteria

After implementation:
- All modified PHP files must have valid syntax (`php -l` passes)
- The code must pass linting (`vendor/bin/pint --test`)
- The code must pass static analysis (`vendor/bin/phpstan analyse`)
- The `domainVerification` and `cookieDomain` resources must be defined via `Http::setResource()`
- The `Utopia\Domains\Domain` class must be imported where used
- Controllers must use `->inject('domainVerification')` and `->inject('cookieDomain')`
- Action signatures must declare `bool $domainVerification` and `?string $cookieDomain`
- Global config patterns for these values must be eliminated
